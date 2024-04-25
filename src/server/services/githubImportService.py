import json
import logging
from typing import List
from db.model.githubOrg import GithubOrg
from db.model.githubRepo import GithubRepo
from db.model.githubUser import GithubUser
from db.model.pullRequest import PullRequest
from db.model.tenant import Tenant
from db.repository.repository import Repository
from events.producer import publish_to_kinesis
from services.githubClient import get_org_repos, get_repo_pull_requests, github_gql_query
from utils import log_exceptions
import app_config

def pull_request_response_to_model(tenant, org, response) -> List[PullRequest]:
    repository = response.data.repository
    pullRequests = repository.pullRequests
    result = []
    for pr in pullRequests.nodes:
        pr = PullRequest(
            id = pr.databaseId,
            tenant_id = tenant.id,
            author = pr.author.login,
            author_id = pr.author.databaseId,
            node_id = pr.id,
            org_id = org.id,
            repository_id = repository.databaseId,
            number=pr.number,
            closed_at=pr.closedAt,
            created_at=pr.createdAt,
            changed_files=pr.changedFiles,
            deletions=pr.deletions,
            additions=pr.additions,
            body=pr.bodyText,
            title=pr.title,
            commits_count=pr.commits.totalCount,
            first_commit_message=pr.commits.nodes[0].commit.message,
            first_commit_date=pr.commits.nodes[0].commit.committedDate,
            review_threads_count=pr.reviewThreads.totalCount,
            comments_count=pr.comments.totalCount,
            url=pr.url, 
            state=pr.state
        )
        result.append(pr)
    return result

def send_message(event_batch, name:str, tenant_id:str, installation_id:str, data:dict):
    def create_event_data(name:str, tenant_id:str, installation_id:str, data:dict):
        body = {                
            "event_type": name,
            "tenant_id": tenant_id,
            "installation_id": installation_id,
            "data": data
        }
        
        data_bytes = json.dumps(body).encode('utf-8')
        return EventData(body=data_bytes)

    event_batch.add(create_event_data(name, tenant_id, installation_id, data))

class GithubImportService:
    def __init__(self, session):
        self.session = session
        self.userRepository = Repository(GithubUser, session)
        self.repoRepository = Repository(GithubRepo, session)
        self.orgRepository = Repository(GithubOrg, session)
        self.tenantRepository = Repository(Tenant, session)
        self.prRepository = Repository(PullRequest, session)

    def process_event(self, event):
        event_type = event["event_type"]
        installation_id = event["installation_id"]
        tenant_id = event["tenant_id"]
        data = event["data"]
        cursor = data.get("cursor", None)
        org_name = data.get("org_name", None)
        
        if event_type == "import_users":
            self._fetch_org_users(tenant_id, installation_id, org_name, cursor)
        elif event_type == "import_teams":
            pass        
        elif event_type == "import_repository":
            self.import_repository(tenant_id, installation_id, data["repo_full_name"])
      
    @log_exceptions(log_args = True)
    def create_import_request(self, tenant, org):
        # with github_import_producer:
        publish_to_kinesis(app_config.IMPORT_STREAM_ARN, str(tenant.id), {"event_type": "import_users", "tenant_id": tenant.id, "installation_id": org.installation_id, "data": {"org_name": org.name}})
        publish_to_kinesis(app_config.IMPORT_STREAM_ARN, str(tenant.id), {"event_type": "import_teams", "tenant_id": tenant.id, "installation_id": org.installation_id, "data": {}})            
        repos_result = get_org_repos(org.installation_id, org.name)
        repositories = repos_result.data.organization.repositories.nodes
        
        while(True):
            for repo in repositories:
                githubRepo = GithubRepo(
                    id = repo.databaseId,
                    tenant_id = tenant.id,
                    org_id = org.id,
                    name = repo.name,
                    node_id= repo.id,
                    private = repo.isPrivate,
                    deleted = False,
                    full_name =  repo.nameWithOwner
                )
                self.repoRepository.upsert(githubRepo)
                # send_message(event_batch, 'import_repository', tenant.id, org.installation_id, {"repo_full_name": repo.nameWithOwner})
                publish_to_kinesis(app_config.IMPORT_STREAM_ARN, str(tenant.id), {"event_type": "import_repository", "tenant_id": tenant.id, "installation_id": org.installation_id, "data": {"repo_full_name": repo.nameWithOwner}})
            pageInfo = repos_result.data.organization.repositories.pageInfo
            if pageInfo.hasNextPage:
                repos_result = get_org_repos(org.installation_id, org.name, pageInfo.endCursor)
            else:
                break

            # github_import_producer.send_batch(event_batch)
   
    def _fetch_org_users(self, tenant_id, installation_id, org_name, cursor=None):
        after = "" if cursor is None else f', after: "{cursor}"'
        query = f"""
            query {{
            organization(login: "{org_name}"{after}) {{
                membersWithRole(first: 100) {{
                    totalCount
                    nodes {{
                        login
                        name
                        avatarUrl
                        email
                        id
                        databaseId
                    }}
                    pageInfo {{
                        endCursor
                        hasNextPage
                    }}
                }}
            }}
            }}
        """

        result = github_gql_query(query, installation_id)
        
        for user in result.data.organization.membersWithRole.nodes:
            githubUser = GithubUser(id=user.databaseId,
                                    node_id=user.id,
                                    tenant_id=tenant_id,
                                    login=user.login,
                                    name=user.name,
                                    avatar_url=user.avatarUrl,
                                    email=user.email)  
                      
            self.userRepository.upsert(githubUser)
        
        pageInfo = result.data.organization.membersWithRole.pageInfo
        logging.info(f"Fetching org users for {org_name} hasNextPage: {pageInfo.hasNextPage}")
        if pageInfo.hasNextPage:
            self._fetch_org_users(tenant_id, org_name, installation_id, pageInfo.endCursor)

    def import_repository(self, tenant_id:int, installation_id:int, full_name:str):
        tenant = self.tenantRepository.get(tenant_id)
        if tenant is None:
            raise Exception(f"Tenant with id {tenant_id} not found")
        orgs = [org for org in tenant.github_orgs if org.installation_id == installation_id]
        
        if len(orgs) == 0:
            raise Exception(f"Organization with installation_id {installation_id} not found")
        
        def import_pull_requests(cursor):
            result = get_repo_pull_requests(installation_id, full_name)
            pageInfo = result.data.repository.pullRequests.pageInfo        
            prs = pull_request_response_to_model(tenant , orgs[0], result)
            for pr in prs:
                if not self.prRepository.get(pr.id, tenant.id):
                    self.session.add(pr)
            return pageInfo
        
        pageInfo = import_pull_requests(None)
        while pageInfo.hasNextPage:
            pageInfo = import_pull_requests(pageInfo.endCursor)
        
        self.session.commit()
