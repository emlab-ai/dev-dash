import datetime
from typing import List
from sqlalchemy import or_
from db.repository import (
    UserRepository,
    PullRequestRepository,
    PullRequestReviewRepository,
)
from db.model import GithubUser, User
from db.repository.repository import Repository


def get_manager_chain(managers, managerId):
    try:
        managerId = int(managerId)
    except ValueError:
        return []
    managerIds = [managerId]

    while True:
        changed = False
        for manager in managers:
            if manager.manager_id in managerIds and manager.id not in managerIds:
                managerIds.append(manager.id)
                changed = True
        if not changed:
            break

    return managerIds


class UsersService:
    def __init__(self, session):
        self.session = session
        self.userRepository = UserRepository(session)
        self.gitUserRepository = Repository(GithubUser, session)

    def get_all_reports(self, tenant_id: int, manager_id: int, directOnly=False):
        manager_id = int(manager_id)
        managers = self.userRepository.list_all_managers(tenant_id)
        if directOnly:
            managerIds = [manager_id]
        else:
            managerIds = get_manager_chain(managers, manager_id)

        return self.userRepository.list_all_reports(tenant_id, managerIds)

    def get_github_user_for_manager_ids(
        self, tenant_id: int, user_ids: List[int]
    ) -> List[int]:

        query = self.session.query(GithubUser)
        query = query.filter(GithubUser.tenant_id == tenant_id)
        query = query.join(User, User.github_user_id == GithubUser.id)
        query = query.filter(or_(User.id.in_(user_ids), User.manager_id.in_(user_ids)))
        # select only the github user ids
        query = query.with_entities(GithubUser.id)

        result = query.all()

        github_user_ids = [user.id for user in result]
        return github_user_ids

    def get_all_users_count(self, tenant_id: int):
        return self.userRepository.count(tenant_id)

    def get_manager_chain(self, tenant_id: int, manager_id: int):
        managers = self.userRepository.list_all_managers(tenant_id)
        return get_manager_chain(managers, manager_id)

    def get_all_mangers(self):
        return self.userRepository.list_all_managers()

    def get_user_details(
        self, tenant_id: int, git_user_id: int, start_date: datetime, end_date: datetime
    ):
        gitUser = self.gitUserRepository.get(git_user_id)
        # user = self.userRepository.find_one(User.github_user_id == git_user_id) #??

        prRepository = PullRequestRepository(self.session)
        prs_count = prRepository.get_count_by_date_user(
            tenant_id, git_user_id, start_date, end_date
        )
        reviewRepository = PullRequestReviewRepository(self.session)
        reviews_count = reviewRepository.get_count_by_date_user(
            tenant_id, git_user_id, start_date, end_date
        )

        return {
            "user": gitUser.to_dict(),
            "prsCount": {"labels": prs_count["labels"], "data": prs_count["data"]},
            "reviewsCount": {
                "labels": reviews_count["labels"],
                "data": reviews_count["data"],
            },
        }
