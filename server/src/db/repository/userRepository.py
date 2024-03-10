from db.model import User
from db.model.pagedResult import PagedResult

class UserRepository:
    def __init__(self, session):
        self.session = session

    def create(self, user):
        try:
            self.session.add(user)
            self.session.commit()
            return user
        except Exception as error:
            print("Error while creating user:", error)

    def get(self, user_id):
        try:
            user = self.session.query(User).filter_by(id=user_id).first()
            return user
        except Exception as error:
            print("Error while getting user:", error)

    def list_all(self, limit=None, after=None, before=None):
        try:
            if before is not None and after is not None:
                raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
            
            query = self.session.query(User)
            if after:
                query = query.filter(User.id > after)
                query = query.order_by(User.id)
            elif before:
                query = query.filter(User.id < before)
                query = query.order_by(User.id.desc())
            

            if limit:
                query = query.limit(limit)
                
            users = query.all()

            before_cursor = None
            after_cursor = None

            if before:
                users = list(reversed(users))

            if users:
                before_cursor = users[0].id
                after_cursor = users[-1].id

            return PagedResult(users, before_cursor, after_cursor)
             
        except Exception as error:
            print("Error while listing users:", error)

    def list_all_reports(self, managerIds):
        try:
            query = self.session.query(User)
            query = query.filter(User.managerId.in_(managerIds))
            reporters = query.all()
            return reporters
        except Exception as error:
            print("Error while listing reporters:", error)

    def list_all_managers(self):
        try:
            query = self.session.query(User)
            query = query.filter(User.isManager == True)

            users = query.all()

            return users
             
        except Exception as error:
            print("Error while listing managers:", error)

    def update(self, user):
        try:
            self.session.merge(user)
            self.session.commit()
        except Exception as error:
            print("Error while updating user:", error)

    def delete(self, user_id):
        try:
            user = self.session.query(User).filter_by(id=user_id).first()
            self.session.delete(user)
            self.session.commit()
        except Exception as error:
            print("Error while deleting user:", error)