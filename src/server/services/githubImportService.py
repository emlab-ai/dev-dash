import logging
from typing import List
from db.model.githubOrg import GithubOrg
from db.model.githubRepo import GithubRepo
from db.model.githubUser import GithubUser
from db.model.pullRequest import PullRequest
from db.model.tenant import Tenant
from db.repository.repository import Repository
from events.producer import publish_to_kinesis
from db.model.githubPullRequestReview import GithubPullRequestReview
from services.githubClient import (
    get_org_repos,
    get_repo_pull_requests2,
    github_gql_query,
)
from utils import log_exceptions
import app_config
from app_logger import logger


def pull_request_response_to_model(tenant, org, node) -> List[PullRequest]:
    if not hasattr(node.author, "databaseId"):
        return None

    return PullRequest(
        id=node.databaseId,
        tenant_id=tenant.id,
        author=node.author.login,
        author_id=node.author.databaseId,
        node_id=node.id,
        org_id=org.id,
        repository_id=node.repository.databaseId,
        number=node.number,
        closed_at=node.closedAt,
        created_at=node.createdAt,
        changed_files=node.changedFiles,
        deletions=node.deletions,
        additions=node.additions,
        body=node.bodyText,
        title=node.title,
        commits_count=node.commits.totalCount,
        first_commit_message=node.commits.nodes[0].commit.message,
        first_commit_date=node.commits.nodes[0].commit.committedDate,
        review_threads_count=node.reviewThreads.totalCount,
        comments_count=node.comments.totalCount,
        url=node.url,
        state=node.state,
    )


class GithubImportService:
    def __init__(self, session, inprocess=False):
        self.session = session
        self.userRepository = Repository(GithubUser, session)
        self.repoRepository = Repository(GithubRepo, session)
        self.orgRepository = Repository(GithubOrg, session)
        self.tenantRepository = Repository(Tenant, session)
        self.prRepository = Repository(PullRequest, session)
        self.inprocess = inprocess

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

    def send_event(self, event_type, tenant_id, installation_id, data):
        if self.inprocess:
            self.process_event(
                {
                    "event_type": event_type,
                    "tenant_id": tenant_id,
                    "installation_id": installation_id,
                    "data": data,
                }
            )
        else:
            publish_to_kinesis(
                app_config.IMPORT_STREAM_ARN,
                str(tenant_id),
                {
                    "event_type": event_type,
                    "tenant_id": tenant_id,
                    "installation_id": installation_id,
                    "data": data,
                },
            )

    @log_exceptions(log_args=True)
    def create_import_request(self, tenant, org):
        self.send_event(
            "import_users", tenant.id, org.installation_id, {"org_name": org.name}
        )
        self.send_event("import_teams", tenant.id, org.installation_id, {})
        repos_result = get_org_repos(org.installation_id, org.name)

        while True:
            repositories = repos_result.data.organization.repositories.nodes
            for repo in repositories:
                githubRepo = GithubRepo(
                    id=repo.databaseId,
                    tenant_id=tenant.id,
                    org_id=org.id,
                    name=repo.name,
                    node_id=repo.id,
                    private=repo.isPrivate,
                    deleted=False,
                    full_name=repo.nameWithOwner,
                )
                self.repoRepository.upsert(githubRepo)
                logger.info(f"Importing repository {repo.nameWithOwner}")
                self.send_event(
                    "import_repository",
                    tenant.id,
                    org.installation_id,
                    {"repo_full_name": repo.nameWithOwner},
                )
            pageInfo = repos_result.data.organization.repositories.pageInfo
            if pageInfo.hasNextPage:
                repos_result = get_org_repos(
                    org.installation_id, org.name, pageInfo.endCursor
                )
            else:
                break

    def _fetch_org_users(self, tenant_id, installation_id, org_name, cursor=None):
        after = "" if cursor is None else f', after: "{cursor}"'
        query = f"""
            query {{
            organization(login: "{org_name}") {{
                membersWithRole(first: 100{after}) {{
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

        ids = [
            user.databaseId for user in result.data.organization.membersWithRole.nodes
        ]
        existing_user_ids = self.userRepository.contains_intersect(tenant_id, ids)

        for user in result.data.organization.membersWithRole.nodes:
            if user.databaseId in existing_user_ids:
                continue

            githubUser = GithubUser(
                id=user.databaseId,
                node_id=user.id,
                tenant_id=tenant_id,
                login=user.login,
                name=user.name,
                avatar_url=user.avatarUrl,
                email=user.email,
            )

            self.userRepository.upsert(githubUser)

        pageInfo = result.data.organization.membersWithRole.pageInfo
        logging.info(
            f"Fetching org users for {org_name} hasNextPage: {pageInfo.hasNextPage}"
        )
        if pageInfo.hasNextPage:
            self._fetch_org_users(
                tenant_id, installation_id, org_name, pageInfo.endCursor
            )

    def import_pull_request_reviews(self, org, node):
        reviewsRepo = Repository(GithubPullRequestReview, self.session)
        ids = [review.databaseId for review in node.reviews.nodes]
        existing_ids = reviewsRepo.contains_intersect(org.tenant.id, ids)
        for review in node.reviews.nodes:
            if review.databaseId in existing_ids:
                continue

            reviewRecord = GithubPullRequestReview(
                id=review.databaseId,
                node_id=review.id,
                tenant_id=org.tenant.id,
                author_id=review.author.databaseId,
                author=review.author.login,
                state=review.state,
                submitted_at=review.submittedAt,
                body=review.bodyText,
                repo_id=node.repository.databaseId,
                pr_id=node.databaseId,
                pr_number=node.number,
                commit_id=None,
                org_id=org.id,
            )

            self.session.add(reviewRecord)

        if node.reviews.pageInfo.hasNextPage:
            print("TODO: import more reviews")
            # TODO: publish event to import more reviews
            pass

    def import_repository(self, tenant_id: int, installation_id: int, full_name: str):
        tenant = self.tenantRepository.get(tenant_id)
        if tenant is None:
            raise Exception(f"Tenant with id {tenant_id} not found")
        orgs = [
            org for org in tenant.github_orgs if org.installation_id == installation_id
        ]

        if len(orgs) == 0:
            raise Exception(
                f"Organization with installation_id {installation_id} not found"
            )

        def import_pull_requests(cursor):
            result = get_repo_pull_requests2(installation_id, full_name, cursor)
            ids = [node.databaseId for node in result.data.search.nodes]
            existing_ids = self.prRepository.contains_intersect(tenant.id, ids)
            for node in result.data.search.nodes:
                pr = pull_request_response_to_model(tenant, orgs[0], node)
                if not pr:
                    continue

                if not (pr.id in existing_ids):
                    self.session.add(pr)

                # self.import_pull_request_review_threads(installation_id, node)
                self.import_pull_request_reviews(orgs[0], node)
                # self.import_pull_request_comments(installation_id, node)
            self.session.commit()

            return result.data.search.pageInfo

        pageInfo = import_pull_requests(None)
        while pageInfo.hasNextPage:
            pageInfo = import_pull_requests(pageInfo.endCursor)

        self.session.commit()
