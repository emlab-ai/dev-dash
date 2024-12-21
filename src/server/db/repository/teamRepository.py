from typing import Optional

from sqlalchemy import select
from db.model.team import Team
from db.model.pagedResult import PagedResult
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

