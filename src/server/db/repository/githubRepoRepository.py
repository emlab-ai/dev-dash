from db.model.githubRepo import GithubRepo
from db.model.pagedResult import PagedResult
from db.repository.repository import Repository, add_cursor_filter, process_paged_result


class GithubRepoRepository(Repository[GithubRepo]):
    def __init__(self, session):
        super().__init__(GithubRepo, session)

    def list_all(
        self,
        tenant_id: int,
        limit=None,
        after=None,
        before=None,
        sort_by: str = None,
        sort_order: str = None,
        name_filter: str = None,
    ):
        if before is not None and after is not None:
            raise ValueError(
                "Both 'before' and 'after' cannot be provided at the same time."
            )

        query = self.session.query(GithubRepo)
        query = query.filter(GithubRepo.tenant_id == tenant_id)

        total_count = query.count()

        if name_filter:
            query = query.filter(GithubRepo.name.ilike(f"%{name_filter}%"))

        query = add_cursor_filter(
            GithubRepo,
            query,
            after,
            before,
            sort_by,
            GithubRepo.id,
            sort_order,
            group=False,
        )

        if limit:
            query = query.limit(limit + 1)

        result = query.all()

        result = [item.to_dict() for item in result]

        result, before_cursor, after_cursor = process_paged_result(
            result, limit, before, after
        )

        return PagedResult(result, total_count, before_cursor, after_cursor)
