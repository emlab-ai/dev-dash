from datetime import datetime, timezone
import json
import logging

from cachetools import TTLCache, cached
from db.model.githubIssue import GithubIssue

from db.model import PullRequest, GithubEvent, GithubRepo, GithubOrg, GithubInstallation, GithubUser,GithubIssueComment, GithubPullRequestReviewComment, GithubPullRequestReview
from db.repository.repository import Repository
from events.producer import publish_to_kinesis
from services.githubImportService import GithubImportService
from utils import log_exceptions
from services.event_helpers import issue_comment_to_model, issue_to_model, pull_request_event_to_model, pull_request_review_comment_to_model, pull_request_review_to_model, repository_to_model
from services.githubClient import github_gql_query
import app_config

tenant_cache = TTLCache(maxsize=10000, ttl=300000)

class GithubWebhookService:
    def __init__(self, session):
        self.session = session
        self.userRepository = Repository(GithubUser, session)

    @log_exceptions(log_args = True)
    def record_event(self, event_type, deliveryId, data):
            body = {
                "data": data,
                "event_type": event_type,
                "delivery_id": deliveryId
            }
            
            publish_to_kinesis(app_config.EVENTS_STREAM_ARN, str(deliveryId), body)      
        
    def process_event(self, event_type, deliveryId, data):
        eventRepo = Repository(GithubEvent, self.session)
        
        if eventRepo.find_one(GithubEvent.delivery_id == deliveryId, GithubEvent.failed == False) is not None:
            return
        
        installationId = data["installation"]["id"]

        try:
            if event_type == "issue_comment":
                self.process_issue_comment(data)
            elif event_type == "pull_request":
                self.process_pull_request(data)
            elif event_type == "pull_request_review_comment":
                self.process_pull_request_review_comment(data)
            elif event_type == "pull_request_review":
                self.process_pull_request_review(data)
            elif event_type == "installation":
                self.process_installation(data)
            elif event_type == "installation_repositories":
                self.process_installation_repositories(data)
            elif event_type == "issues":
                self.process_issues(data)
            
            eventRepo.create(GithubEvent(installation_id = installationId,
                received_at = datetime.utcnow(),
                delivery_id = deliveryId,
                data = data))
        except Exception as e:
            logging.error(f"Failed to process event {event_type} for installation {installationId}, error: {e}")
            eventRepo.create(GithubEvent(installation_id = installationId,
                data=data,
                received_at = datetime.utcnow(),
                failed = True,
                error_text = str(e),
                delivery_id = deliveryId))

        return True

    @cached(tenant_cache)
    def _get_tenant_for_installation(self, installation_id):
        instRepository = Repository(GithubInstallation, self.session)
        inst = instRepository.find_one(GithubInstallation.installation_id == installation_id)
        return inst.tenant if inst else None
    
    def process_issue_comment(self, data):
        installationId = data["installation"]["id"]
        tenant = self._get_tenant_for_installation(installationId)
        action = data["action"]

        commentRepo = Repository(GithubIssueComment, self.session)

        if action == "created" or action == "edited":
            commentRecord = issue_comment_to_model(tenant, data)
            commentRepo.upsert(commentRecord)
        elif action == "deleted":
            commentRepo.delete(data["comment"]["id"])

    def process_installation(self, data):
        installationId = data["installation"]["id"]
        tenant = self._get_tenant_for_installation(installationId)

        if not tenant:
            logging.error(f"Tenant not found for installation {installationId}")
            return

        repoRepository = Repository(GithubRepo, self.session)
        orgRepository = Repository(GithubOrg, self.session)
        instRepository = Repository(GithubInstallation, self.session)
        
        orgJson = data["installation"]["account"]
        org_id = orgJson["id"]
        
        inst = instRepository.find_one(GithubInstallation.installation_id == installationId)
        org = orgRepository.get(org_id, tenant_id = tenant.id)

        if data["action"] == "created":
                       

            if not org:
                org = GithubOrg(
                    id = org_id,
                    tenant_id = tenant.id,                
                    node_id = orgJson["node_id"],
                    name= orgJson["login"],
                    url = orgJson["html_url"],
                    avatar_url= orgJson["avatar_url"],
                    installation_id= installationId,
                    type= orgJson["type"])                
                orgRepository.upsert(org)
                inst.org_id = org_id
                instRepository.update(inst)


            for repo in data["repositories"]:
                repoRepository.upsert(repository_to_model(tenant, org, repo))
                
            GithubImportService(self.session).create_import_request(tenant, org)
        elif data["action"] == "deleted":
            if inst:
                org = orgRepository.get(inst.org_id)
                org.deleted = True
                orgRepository.update(org)
                inst.deleted = True
                instRepository.update(inst)


    def process_installation_repositories(self, data):
        installationId = data["installation"]["id"]
        tenant = self._get_tenant_for_installation(installationId)
        repoRepository = Repository(GithubRepo, self.session)
        orgRepository = Repository(GithubOrg, self.session)
        
        org = orgRepository.find_one(GithubOrg.installation_id == installationId)

        for repo in data["repositories_added"]:
            repoRepository.upsert(repository_to_model(tenant, org, repo))
        
        for repo in data["repositories_removed"]:
            repo = repoRepository.get(repo["id"])
            repo.deleted = True
            repoRepository.update(repo)

    def process_pull_request(self, data):
        action = data["action"]
        pull_request = data["pull_request"]
        installation_id = data["installation"]["id"]
        node_id = pull_request["node_id"]    

        query = f"""
            query {{
            node(id: "{node_id}") {{
                ... on PullRequest {{
                id
                createdAt
                commits(first:1) {{
                    totalCount
                    nodes {{
                        commit  {{
                            committedDate
                            message
                        }}
                    }}
                    }}
                }}                
                }}
            }}
        """

        firstCommitDate = None
        firstCommitMessage = ''

        if action == "closed":
            result = github_gql_query(query, installation_id)

            commit = result.data.node.commits.nodes[0].commit
            firstCommitDate = commit.committedDate
            firstCommitMessage = commit.message

        if not (action == "closed" or action == "opened"):
            return

        tenant = self._get_tenant_for_installation(installation_id)
        prRecord = pull_request_event_to_model(tenant, data)
        prRecord.first_commit_date = firstCommitDate
        prRecord.first_commit_message = firstCommitMessage

        prRepo = Repository(PullRequest, self.session)
        prRepo.upsert(prRecord)

    def process_pull_request_review_comment(self, data):
        installationId = data["installation"]["id"]
        tenant = self._get_tenant_for_installation(installationId)
        action = data["action"]

        commentRepo = Repository(GithubPullRequestReviewComment, self.session)

        if action == "created" or action == "edited":
            commentRecord = pull_request_review_comment_to_model(tenant, data)
            commentRepo.upsert(commentRecord)
        elif action == "deleted":
            commentRepo.delete(data["comment"]["id"])

    def process_pull_request_review(self, data):
        installationId = data["installation"]["id"]
        tenant = self._get_tenant_for_installation(installationId)
        action = data["action"]   
        review = data["review"]
        reviewRepo = Repository(GithubPullRequestReview, self.session)

        if action == "submitted" or action == "edited":
            reviewRecord = pull_request_review_to_model(tenant, data)
            reviewRepo.upsert(reviewRecord)

        elif action == 'dismissed':
            review = reviewRepo.get(review["id"])
            review.state = "dismissed"
            reviewRepo.update(review)

    def process_issues(self, data):
        installationId = data["installation"]["id"]
        tenant = self._get_tenant_for_installation(installationId)
        action = data["action"]
        issue = data["issue"]
        issueRepo = Repository(GithubIssue, self.session)

        if action == "opened" or action == "edited" or action == "reopened":
            issueRecord = issue_to_model(tenant, data)
            issueRepo.upsert(issueRecord)
        elif action == "closed":
            issueRecord = issueRepo.get(issue["id"])
            if issueRecord is None:
                issueRecord = issue_to_model(tenant, data)
                issueRepo.upsert(issueRecord)
                return
            issueRecord.state = "closed"
            issue.closed_at = datetime.utcnow()
            issueRepo.update(issueRecord)
        elif action == "assigned":
            pass
        elif action == "deleted":
            issueRepo.delete(issue["id"])