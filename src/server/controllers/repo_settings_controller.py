from fastapi import APIRouter, Query, Request
from db.model.repoSettings import RepoSettings
from db.repository.repoSettingsRepository import RepoSettingsRepository
from app_context import context_session, context_user

router = APIRouter()


@router.get("/repoSettings")
def list_repo_settings(
    after: str = Query(None),
    before: str = Query(None),
    page_size: int = Query(20),
    filter: str = Query(None),
):
    session = context_session.get()
    user = context_user.get()
    repoSettingsRepository = RepoSettingsRepository(session)
    result = repoSettingsRepository.list_all(
        user.tenant.id, page_size, after=after, before=before, name_filter=filter
    )
    return {
        "before": result.before,
        "after": result.after,
        "data": result.data,
        "page_size": page_size,
    }


@router.post("/repoSettings")
async def create_repo_settings(request: Request):
    data = await request.json()
    session = context_session.get()
    user = context_user.get()

    repository_id = data.get("repositoryId", None)
    if repository_id is None:
        raise ValueError("Repository ID is required")

    repos = RepoSettings(
        review_prompt=data.get("reviewPrompt"),
        disable_tracking=data.get("disableTracking", False),
        enable_description_review=data.get("enableDescriptionReview", False),
        description=data.get("description", None),
        repository_id=repository_id,
        tenant_id=user.tenant.id,
    )

    repoSettingsRepository = RepoSettingsRepository(session)
    result = repoSettingsRepository.create(repos)

    return result.to_dict()


@router.put("/repoSettings")
async def update_repo_settings(request: Request):
    data = await request.json()
    session = context_session.get()
    user = context_user.get()

    repository_id = data.get("repositoryId", None)
    if repository_id is None:
        raise ValueError("Repository ID is required")

    team = RepoSettings(
        id=data.get("id"),
        review_prompt=data.get("reviewPrompt"),
        disable_tracking=data.get("disableTracking", False),
        enable_description_review=data.get("enableDescriptionReview", False),
        description=data.get("description", None),
        repository_id=repository_id,
        tenant_id=user.tenant.id,
    )

    repoSettingsRepository = RepoSettingsRepository(session)
    result = repoSettingsRepository.update(team)

    return result.to_dict()


@router.delete("/repoSettings/{id}")
def delete_repo_settings(id: str):
    session = context_session.get()

    repoSettingsRepository = RepoSettingsRepository(session)
    repoSettingsRepository.delete(id)

    return "", 204
