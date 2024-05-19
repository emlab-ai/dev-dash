from typing import List
from db.model import User, Team
from db.model.pagedResult import PagedResult
from db.repository.repository import Repository, add_cursor_filter, process_paged_result
from sqlalchemy.orm import aliased, joinedload

class UserRepository(Repository[User]):
    def __init__(self, session):
        super().__init__(User, session)

    def list_all(self, tenant_id:int, limit=None, after=None, before=None, sort_by:str=None, sort_order:str=None):
        if before is not None and after is not None:
            raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
        
        query = self.session.query(User)
        query = query.filter(User.tenant_id == tenant_id)   
        
        total_count = query.count()
        
        query = query.options(joinedload(User.manager))
        query = query.options(joinedload(User.team))
            
        query = add_cursor_filter(User, query, after, before, sort_by, User.id, sort_order, group=False)
        
        if limit:
            query = query.limit(limit+1)
            
        result = query.all()

        result = [item.to_dict() for item in result]
        
        result, before_cursor, after_cursor = process_paged_result(result, limit, before, after)

        return PagedResult(result, total_count, before_cursor, after_cursor)

    def list_all_reports(self, tenant_id:int, managerIds:List[int]):
        query = self.session.query(User)
        query = query.filter(User.tenant_id == tenant_id)
        query = query.filter(User.manager_id.in_(managerIds))
        reporters = query.all()
        return reporters
    
    def list_all_managers(self, tenant_id):
        query = self.session.query(User)
        query = query.filter(User.tenant_id == tenant_id)
        query = query.filter(User.is_manager == True)        

        users = query.all()

        return users
