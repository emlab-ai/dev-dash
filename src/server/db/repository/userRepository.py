from db.model import User, Team
from db.model.pagedResult import PagedResult, process_paged_result
from db.repository.repository import Repository, add_cursor_filter
from sqlalchemy.orm import aliased, joinedload

class UserRepository(Repository[User]):
    def __init__(self, session):
        super().__init__(User, session)

    def list_all(self, limit=None, after=None, before=None, sort_by:str=None, sort_order:str=None):
        if before is not None and after is not None:
            raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
        
        query = self.session.query(User)
        total_count = query.count()
        
        query = query.options(joinedload(User.manager))
        query = query.options(joinedload(User.team))
            
        query = add_cursor_filter(User, query, after, before, sort_by, User.id, sort_order)
            
        result = query.all()

        result = [item.to_dict() for item in result]
        
        result, before_cursor, after_cursor = process_paged_result(result, limit, before, after)

        return PagedResult(result, total_count, before_cursor, after_cursor)

    def list_all_reports(self, managerIds):
        query = self.session.query(User)
        query = query.filter(User.manager_id.in_(managerIds))
        reporters = query.all()
        return reporters
    
    def list_all_managers(self):
        query = self.session.query(User)
        query = query.filter(User.is_manager == True)

        users = query.all()

        return users
