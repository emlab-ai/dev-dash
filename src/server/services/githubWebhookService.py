from datetime import datetime, timezone
import logging

from async_lru import alru_cache
from db.model.githubIssue import GithubIssue
from sqlalchemy.ext.asyncio import AsyncSession

from db.model import (
    PullRequest,
    GithubRepo,
    GithubOrg,
    GithubInstallation,
    GithubIssueComment,
    GithubPullRequestReviewComment,
    GithubPullRequestReview,
    Tenant,
)
from events.producer import publish_to_kinesis
from db.model.repoSettings import RepoSettings
from db.repository.githubEventsRepository import GithubEventsRepository
from db.repository.asyncRepository import AsyncRepository
from db.model.metricValue import create_pr_metric_value
from services.aiAgentService import AiAgentService
from services.githubImportService import GithubImportService
from utils import log_exceptions
from services.event_helpers import (
    issue_comment_to_model,
    issue_to_model,
    parse_date_time,
    pull_request_event_to_model,
    pull_request_review_comment_to_model,
    pull_request_review_to_model,
    repository_to_model,
)
from services.githubClient import github_gql_query
import app_config
from app_logger import logger


class GithubWebhookService:
    def __init__(self, session: AsyncSession, inprocess=False):
        self.session = session
        self.inprocess = inprocess

    @log_exceptions(log_args=True)
    async def record_event_async(self, event_type, deliveryId, data):
        body = {"data": data, "event_type": event_type, "delivery_id": deliveryId}

        if self.inprocess:
            await self.process_event_async(event_type, deliveryId, data)
        else:
            publish_to_kinesis(app_config.EVENTS_STREAM_ARN, str(deliveryId), body)

    async def process_event_async(self, event_type, deliveryId, data):
        eventRepo = GithubEventsRepository()

        installationId = data["installation"]["id"]

        tenant = await self._get_tenant_for_installation_async(installationId)
        if not tenant:
            logging.error(f"Tenant not found for installation {installationId}")
            return

        try:
            if event_type == "issue_comment":
                await self.process_issue_comment_async(data)
            elif event_type == "pull_request":
                await self.process_pull_request_async(data)
            elif event_type == "pull_request_review_comment":
                await self.process_pull_request_review_comment_async(data)
            elif event_type == "pull_request_review":
                await self.process_pull_request_review_async(data)
            elif event_type == "installation":
                await self.process_installation_async(data)
            elif event_type == "installation_repositories":
                await self.process_installation_repositories_async(data)
            elif event_type == "issues":
                await self.process_issues_async(data)

            eventRepo.insert(
                tenant_id=tenant.id,
                event_type=event_type,
                delivery_id=deliveryId,
                data=data,
                received_at=datetime.now(timezone.utc),
            )

        except Exception as e:
            logging.error(
                f"Failed to process event {event_type} for installation {installationId}, error: {e}"
            )

            eventRepo.insert(
                tenant_id=tenant.id,
                delivery_id=deliveryId,
                event_type=event_type,
                data=data,
                error_text=str(e),
                failed=True,
                received_at=datetime.now(timezone.utc),
            )

        return True

    @alru_cache(maxsize=32)
    async def _get_tenant_for_installation_async(self, installation_id) -> Tenant | None:
        instRepository = AsyncRepository(GithubInstallation, self.session)
        inst = await instRepository.find_one_async(
            GithubInstallation.installation_id == installation_id,
            expand=["tenant"],
        )

        tenant = inst.tenant if inst else None
        self.session.expunge(tenant)

        return tenant

    async def process_issue_comment_async(self, data):
        installationId = data["installation"]["id"]
        tenant = await self._get_tenant_for_installation_async(installationId)
        action = data["action"]

        commentRepo = AsyncRepository(GithubIssueComment, self.session)

        if action == "created" or action == "edited":
            commentRecord = issue_comment_to_model(tenant, data)
            await commentRepo.upsert_async(commentRecord)
        elif action == "deleted":
            await commentRepo.delete_async(tenant.id, int(data["comment"]["id"]))

    async def process_installation_async(self, data):
        installationId = data["installation"]["id"]
        tenant = await self._get_tenant_for_installation_async(installationId)

        if not tenant:
            logging.error(f"Tenant not found for installation {installationId}")
            return

        repoRepository = AsyncRepository(GithubRepo, self.session)
        orgRepository = AsyncRepository(GithubOrg, self.session)
        instRepository = AsyncRepository(GithubInstallation, self.session)

        orgJson = data["installation"]["account"]
        org_id = orgJson["id"]

        inst = await instRepository.find_one_async(
            GithubInstallation.installation_id == installationId
        )
        org = await orgRepository.get_async(org_id, tenant_id=tenant.id)

        if data["action"] == "created":

            if not org:
                org = GithubOrg(
                    id=org_id,
                    tenant_id=tenant.id,
                    node_id=orgJson["node_id"],
                    name=orgJson["login"],
                    url=orgJson["html_url"],
                    avatar_url=orgJson["avatar_url"],
                    installation_id=installationId,
                    type=orgJson["type"],
                )
                await orgRepository.upsert_async(org)
                inst.org_id = org_id
                await instRepository.update_async(inst)

            for repo in data["repositories"]:
                await repoRepository.upsert_async(
                    repository_to_model(tenant, org, repo)
                )

            GithubImportService(self.session).create_import_request(tenant, org)
        elif data["action"] == "deleted":
            if inst:
                org = await orgRepository.get_async(inst.org_id)
                org.deleted = True
                await orgRepository.update_async(org)
                inst.deleted = True
                await instRepository.update_async(inst)

    async def process_installation_repositories_async(self, data):
        installationId = data["installation"]["id"]
        tenant = await self._get_tenant_for_installation_async(installationId)
        repoRepository = AsyncRepository(GithubRepo, self.session)
        orgRepository = AsyncRepository(GithubOrg, self.session)

        org = await orgRepository.find_one_async(
            GithubOrg.installation_id == installationId
        )

        for repo in data["repositories_added"]:
            await repoRepository.upsert_async(repository_to_model(tenant, org, repo))

        for repo in data["repositories_removed"]:
            repo = await repoRepository.get_async(repo["id"])
            repo.deleted = True
            await repoRepository.update_async(repo)

    async def process_pull_request_async(self, data):
        logger.info("Processing pull request event")

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
        firstCommitMessage = ""

        if action == "closed":
            result = github_gql_query(query, installation_id)

            commit = result.data.node.commits.nodes[0].commit
            firstCommitDate = commit.committedDate
            firstCommitMessage = commit.message

        # if not (action == "closed" or action == "opened"):
        #     return

        tenant = await self._get_tenant_for_installation_async(installation_id)
        prRecord = pull_request_event_to_model(tenant, data)
        logger.info(f"Processing pull request {prRecord.url}")

        prRecord.first_commit_date = parse_date_time(firstCommitDate)
        prRecord.first_commit_message = firstCommitMessage

        settinsRepo = AsyncRepository(RepoSettings, self.session)
        prRepo = AsyncRepository(PullRequest, self.session)
        orgRepo = AsyncRepository(GithubOrg, self.session)
        repoRepo = AsyncRepository(GithubRepo, self.session)
        repo = await repoRepo.get_async(prRecord.repository_id, tenant.id)
        if repo is None:
            logger.info(
                f"Repository not found for tenant {tenant.id} and repository {prRecord.repository_id}"
            )
            # TODO: import unknown repository
            return

        logger.info(
            f"Requset settings for tenant {tenant.id} and repository {prRecord.repository_id}"
        )
        settings = await settinsRepo.find_one_async(
            RepoSettings.repository_id == prRecord.repository_id
            and RepoSettings.tenant_id == tenant.id
        )
        if settings:
            logger.info(
                f"Settings found for tenant {tenant.id} and repository {prRecord.repository_id}"
            )

        if (
            settings
            and settings.disable_tracking
            and not settings.enable_description_review
        ):
            logger.info(
                f"Tracking disabled for tenant {tenant.id} and repository {prRecord.repository_id}"
            )
            return

        org = await orgRepo.get_async(prRecord.org_id, tenant.id)
        if org is None:
            return

        oldPr = await prRepo.get_async(prRecord.id, tenant.id)

        await prRepo.upsert_async(prRecord)

        await self._calculate_pr_metrics_async(tenant, prRecord)

        if settings and settings.review_prompt:
            if oldPr and oldPr.title == prRecord.title and oldPr.body == prRecord.body:
                logger.info(
                    f"PR title and body did not change for tenant {tenant.id} and repository {prRecord.repository_id}"
                )
                return
            logger.info(
                f"Creating PR review request for tenant {tenant.id} and repository {prRecord.repository_id}"
            )
            aiAgetService = AiAgentService(self.session, True)
            await aiAgetService.create_pr_review_request_async(tenant, org, prRecord.id)

        if not (action == "opened"):
            return

    async def process_pull_request_review_comment_async(self, data):
        installationId = data["installation"]["id"]
        tenant = await self._get_tenant_for_installation_async(installationId)
        action = data["action"]

        commentRepo = AsyncRepository(GithubPullRequestReviewComment, self.session)

        if action == "created" or action == "edited":
            commentRecord = pull_request_review_comment_to_model(tenant, data)
            await commentRepo.upsert_async(commentRecord)
        elif action == "deleted":
            await commentRepo.delete_async(data["comment"]["id"])

    async def process_pull_request_review_async(self, data):
        installationId = data["installation"]["id"]
        tenant = await self._get_tenant_for_installation_async(installationId)
        action = data["action"]
        review = data["review"]
        reviewRepo = AsyncRepository(GithubPullRequestReview, self.session)

        if action == "submitted" or action == "edited":
            reviewRecord = pull_request_review_to_model(tenant, data)
            await reviewRepo.upsert_async(reviewRecord)

        elif action == "dismissed":
            review = await reviewRepo.get_async(review["id"])
            review.state = "dismissed"
            await reviewRepo.update_async(review)

    async def process_issues_async(self, data):
        installationId = data["installation"]["id"]
        tenant = await self._get_tenant_for_installation_async(installationId)
        action = data["action"]
        issue = data["issue"]
        issueRepo = AsyncRepository(GithubIssue, self.session)

        if action == "opened" or action == "edited" or action == "reopened":
            issueRecord = issue_to_model(tenant, data)
            await issueRepo.upsert_async(issueRecord)
        elif action == "closed":
            issueRecord = await issueRepo.get_async(issue["id"])
            if issueRecord is None:
                issueRecord = issue_to_model(tenant, data)
                await issueRepo.upsert_async(issueRecord)
                return
            issueRecord.state = "closed"
            issue.closed_at = datetime.utcnow()
            await issueRepo.update_async(issueRecord)
        elif action == "assigned":
            pass
        elif action == "deleted":
            await issueRepo.delete_async(issue["id"])

    async def _calculate_pr_metrics_async(
        self, tenant: Tenant, pr: PullRequest
    ):
        logger.info(f"Calculating PR metrics for PR {pr.id}")
        if pr.state != "merged":
            return

        duration = pr.closed_at - pr.created_at

        metric = create_pr_metric_value(
            tenant.id,
            duration.total_seconds() / 3600,
            pr.additions + pr.deletions,
            pr.id,
            pr.author_id,
            pr.repository_id,
        )

        self.session.add(metric)

        pass
