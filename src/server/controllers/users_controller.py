from fastapi import APIRouter, Query, Request
from db.model.user import User
from db.repository.userRepository import UserRepository
from app_context import context_session, context_user
from controllers.utils import _get_request_date_args
from db.repository.pullRequestReviewRepository import PullRequestReviewRepository
from services.userService import UsersService

router = APIRouter()


@router.post("/users")
async def create_user(request: Request):
    session = context_session.get()
    user = context_user.get()
    userRepository = UserRepository(session)

    data = await request.json()
    user_data = User.from_dict(data)
    user_data.tenant_id = user.tenant.id
    user = userRepository.create(user_data)
    return user.to_dict()


@router.delete("/users/{id}")
def delete_user(id: str):
    session = context_session.get()
    userRepository = UserRepository(session)
    userRepository.delete(id)

    return "", 204


@router.put("/users")
async def update_user(request: Request):
    session = context_session.get()
    userRepository = UserRepository(session)
    user = context_user.get()
    data = await request.json()
    user_data = User.from_dict(data)
    user_data.tenant_id = user.tenant.id
    user = userRepository.update(user_data)
    user = userRepository.get(
        user.id, tenant_id=user.tenant.id, expand=["manager", "team"]
    )
    return user.to_dict()


@router.get("/users")
def list_users(
    after: str = Query(None),
    before: str = Query(None),
    page_size: int = Query(20),
    filter: str = Query(None),
):
    session = context_session.get()
    user = context_user.get()
    userRepository = UserRepository(session)
    result = userRepository.list_all(
        user.tenant.id, limit=page_size, after=after, before=before, user_filter=filter
    )
    return {
        "before": result.before,
        "after": result.after,
        "data": result.data,
        "page_size": page_size,
    }


@router.get("/users/{gid}/stats")
def get_users_details(request: Request, gid: int):
    start_date, end_date = _get_request_date_args(request)
    session = context_session.get()
    user = context_user.get()
    userService = UsersService(session)
    result = userService.get_user_details(user.tenant.id, gid, start_date, end_date)

    return result


@router.get("/users/{gid}/reviews")
def get_users_reviews(
    request: Request,
    gid: int,
    after=Query(None),
    before=Query(None),
    page_size: int = Query(20),
):
    start_date, end_date = _get_request_date_args(request)
    session = context_session.get()
    user = context_user.get()
    reviewsRepo = PullRequestReviewRepository(session)
    result = reviewsRepo.list_all(
        tenant_id=user.tenant.id,
        user_id=gid,
        start_date=start_date,
        end_date=end_date,
        limit=page_size,
        after=after,
        before=before,
    )

    return {
        "before": result.before,
        "after": result.after,
        "data": result.data,
        "page_size": 20,
        "total_count": result.total_count,
    }
