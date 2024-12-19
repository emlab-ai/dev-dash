from typing import Optional

from sqlalchemy import select
from db.model.team import Team
from db.model.pagedResult import PagedResult
from db.repository.repository import process_paged_result
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from db.repository.asyncRepository import AsyncRepository


class TeamRepository(AsyncRepository[Team]):
    def __init__(self, session: AsyncSession):
        super().__init__(Team, session)

    async def list_all_async(
        self,
        tenant_id: int,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        order_by: Optional[str] = None,
        sort_order="asc",
    ) -> PagedResult[Team]:

        def build_query():
            ParentTeam = aliased(Team)

            query = select(
                Team.id,
                Team.name,
                Team.parent_id,
                Team.github_team_id,
                Team.tags,
                ParentTeam.name.label("parentName"),
            )

            query = query.filter(Team.tenant_id == tenant_id)
            query = query.outerjoin(ParentTeam, Team.parent_id == ParentTeam.id)
            return query

        def build_order():
            return Team.id

        return await super()._list_all_async(
            build_query,
            build_order,
            limit,
            after,
            before,
            sort_by=order_by,
            sort_order=sort_order,
        )

        try:
            if before is not None and after is not None:
                raise ValueError(
                    "Both 'before' and 'after' cannot be provided at the same time."
                )

            ParentTeam = aliased(Team)
            query = self.session.query(Team, ParentTeam)
            query = query.filter(Team.tenant_id == tenant_id)
            query = query.outerjoin(ParentTeam, Team.parent_id == ParentTeam.id)

            total_count = query.count()

            if after:
                query = query.filter(Team.id > after)
                query = query.order_by(Team.id.asc())
            elif before:
                query = query.filter(Team.id < before)
                query = query.order_by(Team.id.desc())
            else:
                query = query.order_by(Team.id.asc())

            if limit:
                query = query.limit(limit + 1)

            query = query.with_entities(
                Team.id,
                Team.name,
                Team.parent_id,
                Team.github_team_id,
                Team.tags,
                ParentTeam.name.label("parentName"),
            )

            result = query.all()
            result = [item._asdict() for item in result]

            result, before_cursor, after_cursor = process_paged_result(
                result, limit, before, after
            )

            return PagedResult(result, total_count, before_cursor, after_cursor)
        except Exception as error:
            print("Error while listing git_stats:", error)
            raise error
