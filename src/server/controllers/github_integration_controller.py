from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse
from db.model.githubInstallation import GithubInstallation
from db.repository.repository import Repository
from services.githubWebhookService import GithubWebhookService
from app_context import context_session
from app_logger import logger

router = APIRouter()


@router.post("/wh")
async def github_wh_callback(request: Request):
    event = request.headers.get("X-GitHub-Event")
    deliveryId = request.headers.get("X-GitHub-Delivery")
    # signature = request.headers.get("X-Hub-Signature-256")
    userAgent = request.headers.get("User-Agent")
    session = context_session.get()

    if not userAgent.startswith("GitHub-Hookshot/"):
        print(f"Invalid user agent: {userAgent}")
        return "", 404

    data = await request.json()

    githubService = GithubWebhookService(session)
    # TODO: vlidate signature
    githubService.record_event(event, deliveryId, data)

    return "", 200


@router.get("/installation")
def register_installation_id(
    installation_id: str = Query(None),
    setup_action: str = Query(None),
    state: str = Query(None),
):
    session = context_session.get()
    installationRepository = Repository(GithubInstallation, session)
    if setup_action == "install":

        inst = installationRepository.find_one(
            GithubInstallation.installation_token == state
        )
        if inst is None:
            logger.error("Invalid installation token")
            return RedirectResponse(url="/404")

        if inst.installation_id is not None:
            logger.error("Installation token already used")
            return RedirectResponse(url="/settings/github")

        inst.installation_id = installation_id
        inst.installation_token = None

        installationRepository.update(inst)

    return RedirectResponse(url="/settings/organisation")
