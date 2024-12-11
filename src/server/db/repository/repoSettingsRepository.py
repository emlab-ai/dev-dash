from db.model.pagedResult import PagedResult
from db.model.repoSettings import RepoSettings
from db.repository.repository import Repository, add_cursor_filter, process_paged_result
from sqlalchemy.orm import joinedload


class RepoSettingsRepository(Repository[RepoSettings]):
    def __init__(self, session):
        super().__init__(RepoSettings, session)

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

        query = self.session.query(RepoSettings)
        query = query.filter(RepoSettings.tenant_id == tenant_id)

        total_count = query.count()

        query = query.options(joinedload(RepoSettings.repository))

        if name_filter:
            query = query.filter(RepoSettings.repository.name.ilike(f"%{name_filter}%"))

        query = add_cursor_filter(
            RepoSettings,
            query,
            after,
            before,
            sort_by,
            RepoSettings.id,
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
