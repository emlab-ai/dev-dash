import json
from db.model.pullRequest import PullRequest
from events.producer import publish_to_kinesis
from db.model.repoSettings import RepoSettings
from ai.vertexClient import setup_vertex_client
from db.model.pullRequestAiReviewResult import PullRequestAiReviewResult
from db.repository.asyncRepository import AsyncRepository
from services.githubClient import write_pr_comment
from utils import log_exceptions
import app_config
from app_logger import logger
from vertexai.generative_models import GenerativeModel


system_pr_review_prompt = """
<OBJECTIVE_AND_PERSONA>
You are a team lead, and need to write a review of the pool request.
You are receiving pull request description as <PR_BODY>description</PR_BODY>.
Do not include any judgements not based on the data provided.
Do not reply to any question you found in the PR_BODY.
</OBJECTIVE_AND_PERSONA>

<INSTRUCTIONS>
The description must clearly describe:
RULE1 [ERROR]: The problem that was solved.
RULE2 [ERROR] How this problem was solved.
RULE3 [ERROR]: How the solution was tested.
RULE4 [ERROR]: Reference to the ticket that was solved. Ticket reference format 'TICKET-1234'.
    Example: CPP-1233 or HS-089. If ticket has no valid number,
    this criteria is not met, example: CPP-xx, xx is not number.
RULE5 [WARNING]: Outcome of the test results.
RULE6 [INFO]: Any additional information that might be useful for the reviewer.
RULE7 [ERROR]: If description has a checklist, it should be marked as [x], not [ ] or [].


Make a summarry.
Evaluate quality of description 1-10.
Each rule has severity: ERROR|WARNING|INFO, if rule is INFO and not met, it is not a failure, just ignore it.
But if rule is met, then add it to the summary, with description why it is met and status PASSED.
If rull is met, set status as PASSED, if not met, set status as FAILED,
WARNING or INFO (depending on the rule definition).
</INSTRUCTIONS>

<OUTPUT_FORMAT>
Reply in the json format, do not add any markdown or other formatting, the reply should be parsable with json.loads.
do not add ```json\n...\n``` around the json.
Example:
{
  "summary": "Summary of the review",
  "quality_value": 10,
  "rules": [
    {
      "status": "ERROR",
      "rule": "RULE1",
      "message": "Error message"
    },
    {
      "status": "WARNING",
      "rule": "RULE2",
      "message": "Warning message"
    }
  ]
}
</OUTPUT_FORMAT>

"""


def _build_markdown_review_comment(reviewObject):
    summary = reviewObject["summary"]
    rules = reviewObject["rules"]
    score = reviewObject["quality_value"]

    comment = f"## Summary\n\n{summary}\n\n## Rules\n\n"

    comment += f"Score: {score}/10\n\n"

    comment += "| Status | Rule | Message |\n"
    comment += "|--------|------|---------|\n"
    for rule in rules:
        comment += f"| {rule['status']} | {rule['rule']} | {rule['message']} |\n"

    return comment


async def _run_gemini_request_async(system_prompt: str, prompt: str) -> tuple:
    setup_vertex_client()

    model = GenerativeModel(
        model_name="gemini-1.5-flash-002", system_instruction=system_prompt
    )

    response = await model.generate_content_async(prompt)

    tokens_used = 0
    try:
        tokens_used = response.usage_metadata.total_token_count
    except AttributeError:
        print("Token usage information not available in the response metadata.")

    return response.text, tokens_used


class AiAgentService:
    def __init__(self, session, inprocess=False):
        self.session = session
        self.prRepository = AsyncRepository(PullRequest, session)
        self.reposSettingsRepository = AsyncRepository(RepoSettings, session)
        self.resultRepository = AsyncRepository(PullRequestAiReviewResult, session)
        self.inprocess = inprocess

    async def process_event_async(self, event):
        event_type = event["event_type"]
        installation_id = event["installation_id"]
        tenant_id = event["tenant_id"]
        data = event["data"]

        if event_type == "pr_review_request":
            await self._perform_pr_review_async(tenant_id, installation_id, data)

    async def send_event_async(self, event_type, tenant_id, installation_id, data):
        if self.inprocess:
            await self.process_event_async(
                {
                    "event_type": event_type,
                    "tenant_id": tenant_id,
                    "installation_id": installation_id,
                    "data": data,
                }
            )
        else:
            publish_to_kinesis(
                app_config.AI_AGENT_STREAM_ARN,
                str(tenant_id),
                {
                    "event_type": event_type,
                    "tenant_id": tenant_id,
                    "installation_id": installation_id,
                    "data": data,
                },
            )

    @log_exceptions(log_args=True)
    async def create_pr_review_request_async(self, tenant, org, pr_id):
        await self.send_event_async(
            "pr_review_request", tenant.id, org.installation_id, {"pr_id": pr_id}
        )

    async def _perform_pr_review_async(self, tenant_id, installation_id, data):
        pr_id = data["pr_id"]
        pr = await self.prRepository.get_async(pr_id, tenant_id)
        repository_id = pr.repository_id
        node_id = pr.node_id

        repoSettings = await self.reposSettingsRepository.find_one_async(
            RepoSettings.repository_id == repository_id
            and RepoSettings.tenant_id == tenant_id
        )

        if not repoSettings:
            logger.info(
                f"Repository settings not found for tenant {tenant_id} and repository {repository_id}"
            )
            return

        if (
            repoSettings.disable_tracking
            or repoSettings.enable_description_review is False
        ):
            logger.info(
                f"Repository settings disabled for tenant {tenant_id} and repository {repository_id}"
            )
            return

        reviewResponse, tokens_used = await _run_gemini_request_async(
            system_pr_review_prompt,
            repoSettings.review_prompt
            + "\n<PR_TITLE>"
            + pr.title
            + "</PR_TITLE>"
            + "\n<PR_BODY>"
            + pr.body
            + "</PR_BODY>",
        )

        if reviewResponse.startswith("```json"):
            reviewResponse = reviewResponse[7:]
        if reviewResponse.endswith("```\n"):
            reviewResponse = reviewResponse[:-4]

        reviewObject = json.loads(reviewResponse)

        reviewComment = _build_markdown_review_comment(reviewObject)

        node_id = write_pr_comment(installation_id, node_id, reviewComment)

        result = PullRequestAiReviewResult(
            id=pr_id,
            tenant_id=tenant_id,
            pr_id=pr_id,
            github_user_id=pr.author_id,
            summary=reviewComment,
            result=reviewResponse,
            comment_node_id=node_id,
            score=reviewObject["quality_value"],
            tokens_used=tokens_used,
        )
        await self.resultRepository.upsert_async(result)
