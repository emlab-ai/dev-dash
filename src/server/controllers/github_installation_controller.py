import uuid
from fastapi import APIRouter, Request
from db.model.githubInstallation import GithubInstallation
from db.repository.repository import Repository
from db.model.githubOrg import GithubOrg
from services.githubImportService import GithubImportService
from app_context import context_session, context_user

router = APIRouter()


@router.post("/github/installation")
def init_register_installation_id():
    session = context_session.get()
    user = context_user.get()
    installationRepository = Repository(GithubInstallation, session)
    inst = installationRepository.create(
        GithubInstallation(
            tenant_id=user.tenant.id, installation_token=str(uuid.uuid4())
        )
    )

    return {"state": inst.installation_token}


@router.delete("/github/installation/{id}")
def delete_installation_id():
    # TODO: this was never implemented
    # session = context_session.get()
    # user = context_user.get()
    # installationRepository = Repository(GithubInstallation, session)
    # inst = installationRepository.create(
    #               GithubInstallation(tenant_id=user.tenant.id, installation_token=str(uuid.uuid4())))

    return {"state": ""}, 501  # inst.installation_token


@router.post("/github/installation/import")
async def import_installation(request: Request):
    body = await request.json()
    session = context_session.get()
    user = context_user.get()
    orgRepository = Repository(GithubOrg, session)
    org = orgRepository.find_one(
        GithubOrg.installation_id == body["installation_id"],
        GithubOrg.tenant_id == user.tenant.id,
    )

    if org is None:
        return "", 404

    GithubImportService(session).create_import_request(org.tenant, org)

    return "", 201
