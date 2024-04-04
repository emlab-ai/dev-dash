from db.model import User, Team
from db.model.pagedResult import PagedResult, process_paged_result
from sqlalchemy.orm import aliased

class UserRepository:
    def __init__(self, session):
        self.session = session

    def create(self, user):
        self.session.add(user)
        self.session.commit()
        return user

    def get(self, user_id):
        user = self.session.query(User).filter(User.id == user_id).first()
        return user

    def get_by_email(self, email):
        user = self.session.query(User).filter(User.email == email).first()
        return user

    def list_all(self, limit=None, after=None, before=None):
        if before is not None and after is not None:
            raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
        
        query = self.session.query(User)
        total_count = query.count()
        Manager = aliased(User)
        query = query.outerjoin(Manager, User.manager_id == Manager.id)
        query = query.outerjoin(Team, User.team_id == Team.id)

        if after:
            query = query.filter(User.id >= after)
            query = query.order_by(User.id)
        elif before:
            query = query.filter(User.id < before)
            query = query.order_by(User.id.desc())
        else:
            query = query.order_by(User.id)

        if limit:
            query = query.limit(limit+1)
            
        result = query.all()

        query = query.with_entities(
            User.id,
            User.name,
            User.manager_id,
            User.email,
            User.is_manager,
            User.team_id,
            User.github_user,
            User.github_user_id,
            User.tags,
            User.level,
            User.tags,
            Manager.name.label('manager_name'),
            Team.name.label('team_name')
        )
        
        result = query.all()
        result = [item._asdict() for item in result]
        
        result, before_cursor, after_cursor = process_paged_result(result, limit, before, after)

        return PagedResult(result, total_count, before_cursor, after_cursor)

    def list_all_reports(self, managerIds):
        query = self.session.query(User)
        query = query.filter(User.manager_id.in_(managerIds))
        reporters = query.all()
        return reporters
    
    def count(self):
        query = self.session.query(User)
        return query.count()

    def list_all_managers(self):
        query = self.session.query(User)
        query = query.filter(User.is_manager == True)

        users = query.all()

        return users

    def update(self, user):
        self.session.merge(user)
        self.session.commit()
        return user

    def delete(self, user_id):
        user = self.session.query(User).filter_by(id=user_id).first()
        self.session.delete(user)
        self.session.commit()