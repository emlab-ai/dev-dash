import datetime
from db.repository import UserRepository, PullRequestRepository, PullRequestReviewRepository

def get_manager_chain(managers, managerId):
    managerId = int(managerId)
    managerIds = [managerId]

    while True:
        changed = False
        for manager in managers:
            if manager.managerId in managerIds and manager.id not in managerIds:
                managerIds.append(manager.id)
                changed = True
        if not changed:
            break

    return managerIds

class UsersService:
    def __init__(self, session):
        self.session = session
        self.userRepository = UserRepository(session)
    
    def get_all_reports(self, managerId, directOnly=False):        
        managerId = int(managerId)
        managers = self.userRepository.list_all_managers()
        if directOnly:
            managerIds = [managerId]
        else:
            managerIds = get_manager_chain(managers, managerId)

        return self.userRepository.list_all_reports(managerIds)
    
    def get_all_users_count(self):
        return self.userRepository.count()
    
    def get_manager_chain(self, managerId):
        managers = self.userRepository.list_all_managers()
        return get_manager_chain(managers, managerId)
    
    def get_all_mangers(self):
        return self.userRepository.list_all_managers()
    
    def get_user_details(self, user_id:int, start_date:datetime, end_date:datetime):
        user = self.userRepository.get(user_id).to_dict()
        prRepository = PullRequestRepository(self.session)
        prs_count = prRepository.get_count_by_date_user(user_id, start_date, end_date)
        reviewRepository = PullRequestReviewRepository(self.session)
        reviews_count = reviewRepository.get_count_by_date_user(user_id, start_date, end_date)
 
        return {
            "user": user,
            "prsCount": {
                "labels":prs_count["labels"],
                "data": prs_count["data"]
            },
            "reviewsCount": {
                "labels":reviews_count["labels"],
                "data": reviews_count["data"]
            }
        }