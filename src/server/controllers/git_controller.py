from fastapi import APIRouter, Query, Request
from app_context import context_session, context_user
from controllers.utils import _get_request_scope_args
from db.model.githubRepo import GithubRepo
from db.repository.githubRepoRepository import GithubRepoRepository
from db.repository.githubUserRepository import GithubUserRepository
from db.repository.pullRequestRepository import PullRequestRepository
from db.repository.repository import Repository
from services.statsService import StatsService
from services.userService import UsersService

router = APIRouter()


@router.get("/git/users")
def get_git_users(
    after: str = Query(None), before: str = Query(None), page_size: int = Query(20)
):
    session = context_session.get()
    user = context_user.get()

    userRepository = GithubUserRepository(session)
    result = userRepository.list_all(
        user.tenant.id, limit=page_size, after=after, before=before
    )
    return {
        "before": result.before,
        "after": result.after,
        "data": result.data,
        "page_size": page_size,
    }


@router.get("/git/repos")
def get_git_repos(
    after: str = Query(None),
    before: str = Query(None),
    page_size: int = Query(20),
    filter: str = Query(None),
):
    session = context_session.get()
    user = context_user.get()
    repoRepository = GithubRepoRepository(session)
    result = repoRepository.list_all(
        user.tenant.id, limit=page_size, after=after, before=before, name_filter=filter
    )
    return {
        "before": result.before,
        "after": result.after,
        "data": result.data,
        "page_size": page_size,
    }


@router.get("/git/repos/{gid}")
def get_git_repo_details(gid: int):
    session = context_session.get()
    user = context_user.get()
    gitRepoService = Repository(GithubRepo, session)
    result = gitRepoService.get(gid, user.tenant.id)

    return result


@router.get("/git/prs")
def get_git_prs(
    request: Request,
    after: str = Query(None),
    before: str = Query(None),
    page_size: int = Query(20),
    user_id: str = Query(None),
    repo_id: str = Query(None),
    sort_by: str = Query(alias="s", default="closed_at"),
    sort_order: str = Query(alias="so", default="desc"),
):
    session = context_session.get()
    user = context_user.get()
    manager_id, start_date, end_date = _get_request_scope_args(request)

    prRepository = PullRequestRepository(session)
    userService = UsersService(session)

    managers_ids = None
    github_users_ids = None
    if manager_id is not None:
        # todo: find user id for manger_id which is github user id

        managers_ids = userService.get_manager_chain(user.tenant.id, manager_id)
        github_users_ids = userService.get_github_user_for_manager_ids(
            user.tenant.id, managers_ids
        )

    user_ids = None
    if user_id is not None:
        user_id = int(user_id)
        user_ids = [user_id]
        github_users_ids = user_ids

    page_size = min(int(page_size), 50)
    result = prRepository.list_all(
        tenant_id=user.tenant.id,
        limit=page_size,
        start_date=start_date,
        end_date=end_date,
        github_users_ids=github_users_ids,
        github_repo_id=repo_id,
        after=after,
        before=before,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    data = [
        {
            "id": pr["id"],
            "author": pr["author"],
            "authorId": pr["author_id"],
            "nodeId": pr["node_id"],
            "number": pr["number"],
            "closedAt": pr["closed_at"],
            "createdAt": pr["created_at"],
            "changedFiles": pr["changed_files"],
            "deletions": pr["deletions"],
            "additions": pr["additions"],
            "body": pr["body"],
            "title": pr["title"],
            "commitsCount": pr["commits_count"],
            "firstCommitMessage": pr["first_commit_message"],
            "firstCommitDate": pr["first_commit_date"],
            "reviewThreadsCount": pr["review_threads_count"],
            "commentsCount": pr["comments_count"],
            "url": pr["url"],
            "changes": pr["changes"],
            "totalDuration": pr["total_duration"],
            "state": pr["state"],
        }
        for pr in result.data
    ]

    git_stats = {
        "before": result.before,
        "after": result.after,
        "data": data,
        "page_size": page_size,
        "total_count": result.total_count,
    }

    return git_stats


@router.get("/git/prs_stats")
def get_git_prs_stats(request: Request):
    session = context_session.get()
    user = context_user.get()
    managerId, start_date, end_date = _get_request_scope_args(request)

    prRepository = PullRequestRepository(session)
    userService = UsersService(session)
    managerIds = None
    github_user_ids = None
    if managerId is not None:
        managerIds = userService.get_manager_chain(user.tenant.id, managerId)
        github_user_ids = userService.get_github_user_for_manager_ids(
            user.tenant.id, managerIds
        )

    result = prRepository.get_avg_stats(
        user.tenant.id,
        start_date=start_date,
        end_date=end_date,
        github_user_ids=github_user_ids,
    )

    git_stats = {
        "count": result.count,
        "avg_loc": result.avg_loc,
        "avg_duration": result.avg_duration,
        "avg_files_changed": result.avg_files_changed,
        "avg_comments_count": result.avg_comments_count,
    }

    return git_stats


@router.get("/git/user_stats")
def get_users_stats(
    request: Request,
    after: str = Query(None),
    before: str = Query(None),
    page_size: int = Query(20),
    sort_by: str = Query(alias="s", default="id"),
    sort_order: str = Query(alias="so", default="desc"),
):

    managerId, start_date, end_date = _get_request_scope_args(request)
    session = context_session.get()
    user = context_user.get()

    userService = UsersService(session)
    statsService = StatsService(session)

    managerIds = None
    userIds = None
    if managerId is not None:
        managerIds = userService.get_manager_chain(user.tenant.id, managerId)
        userIds = userService.get_github_user_for_manager_ids(
            user.tenant.id, managerIds
        )

    result = statsService.build_user_stats(
        user.tenant.id,
        userIds,
        start_date,
        end_date,
        page_size,
        after,
        before,
        sort_by,
        sort_order,
    )

    return result


@router.get("/git/repo_stats")
def get_repos_stats(
    request: Request,
    after: str = Query(None),
    before: str = Query(None),
    page_size: int = Query(20),
    sort_by: str = Query(alias="s", default="id"),
    sort_order: str = Query(alias="so", default="desc"),
):
    managerId, start_date, end_date = _get_request_scope_args(request)
    session = context_session.get()
    user = context_user.get()
    userService = UsersService(session)
    statsService = StatsService(session)

    managerIds = None
    userIds = None
    if managerId is not None:
        managerIds = userService.get_manager_chain(user.tenant.id, managerId)
        userIds = userService.get_github_user_for_manager_ids(
            user.tenant.id, managerIds
        )

    result = statsService.build_repo_stats(
        user.tenant.id,
        userIds,
        start_date,
        end_date,
        page_size,
        after,
        before,
        sort_by,
        sort_order,
    )

    return result
