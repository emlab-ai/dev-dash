from fastapi import APIRouter, Query, Request
from db.model.team import Team
from db.repository.teamRepository import TeamRepository
from utils import none_if_empty
from app_context import context_session, context_user

router = APIRouter()


@router.get("/teams")
def get_teams(
    after: str = Query(None), before: str = Query(None), page_size: int = Query(20)
):
    session = context_session.get()
    user = context_user.get()
    teamsRepo = TeamRepository(session)
    result = teamsRepo.list_all(
        user.tenant.id, limit=page_size, after=after, before=before
    )

    return {
        "before": result.before,
        "after": result.after,
        "data": result.data,
        "page_size": page_size,
        "total_count": result.total_count,
    }


@router.post("/teams")
async def create_team(request: Request):
    data = await request.json()
    session = context_session.get()
    user = context_user.get()

    team = Team(
        name=data.get("name"),
        parent_id=none_if_empty(data.get("parentId", None)),
        tenant_id=user.tenant.id,
    )

    teamsRepo = TeamRepository(session)
    result = teamsRepo.create_team(team)

    return result.to_dict()


@router.put("/teams")
async def update_team(request: Request):
    data = await request.json()
    team = Team(**data)
    session = context_session.get()
    user = context_user.get()
    team.tenant_id = user.tenant.id

    teamsRepo = TeamRepository(session)
    result = teamsRepo.update_team(team)

    return result.to_dict()


@router.delete("/teams/{id}")
def delete_team(id: str):
    session = context_session.get()
    teamsRepo = TeamRepository(session)
    teamsRepo.delete_team(id)

    return "", 204
