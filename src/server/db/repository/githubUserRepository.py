from db.model import GithubUser
from db.model.pagedResult import PagedResult
from db.repository.repository import Repository, add_cursor_filter, process_paged_result

class GithubUserRepository(Repository[GithubUser]):
    def __init__(self, session):
        super().__init__(GithubUser, session)

    def list_all(self, tenant_id:int, limit=None, after=None, before=None, sort_by:str=None, sort_order:str=None):
        if before is not None and after is not None:
            raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
        
        query = self.session.query(GithubUser)
        query = query.filter(GithubUser.tenant_id == tenant_id)
        total_count = query.count()
        
        query = add_cursor_filter(GithubUser, query, after, before, sort_by, GithubUser.id, sort_order)
            
        result = query.all()

        result = [item.to_dict() for item in result]
        
        result, before_cursor, after_cursor = process_paged_result(result, limit, before, after)

        return PagedResult(result, total_count, before_cursor, after_cursor)