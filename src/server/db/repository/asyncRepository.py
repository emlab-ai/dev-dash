import base64
import pickle
from typing import Any, Callable, Generic, List, Optional, Sequence, Type, TypeVar, Protocol
from sqlalchemy import Column, ColumnExpressionArgument, Select, and_, func, or_, select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from db.model.pagedResult import PagedResult


class Entity(Protocol):
    id: Column[int]
    tenant_id: Column[int]


T = TypeVar("T", bound=Entity)
QueryT = Select[tuple[T]]


def encode_cursor(id, sort_by: str, sort_by_value) -> str:
    cursor = {"id": id}
    if sort_by:
        cursor[sort_by] = sort_by_value

    pickled_data = pickle.dumps(cursor)
    return base64.urlsafe_b64encode(pickled_data).decode("utf-8")


def decode_cursor(cursor: str) -> dict:
    decoded_string = base64.urlsafe_b64decode(cursor)
    return pickle.loads(decoded_string)


def apply_joinedload(model, query: QueryT, expand: List[str] | None) -> QueryT:
    if expand:
        for expandedProp in expand:
            query = query.options(joinedload(getattr(model, expandedProp)))

    return query


def add_cursor_filter(
    model: Type[T],
    query,
    after: str | None,
    before: str | None,
    sort_by: list[str] | None,
    orderAttr: Column,
    sort_order: str | None,
    group: bool = False,
):

    filterFunc = query.having if group else query.filter
    if after:
        after_cursor = decode_cursor(after)
        afterId = after_cursor["id"]
        afterSortBy = after_cursor[sort_by] if sort_by in after_cursor else None

        if sort_by:
            if sort_order == "asc":
                query = filterFunc(
                    or_(
                        (orderAttr > afterSortBy),
                        and_((orderAttr == afterSortBy), (model.id > afterId)),
                    )
                )
                query = query.order_by(orderAttr.asc(), model.id.asc())
            else:
                query = filterFunc(
                    or_(
                        (orderAttr < afterSortBy),
                        and_((orderAttr == afterSortBy), (model.id < afterId)),
                    )
                )
                query = query.order_by(orderAttr.desc(), model.id.desc())
        else:
            query = filterFunc(model.id > afterId)
            query = query.order_by(
                model.id.desc() if sort_order == "desc" else model.id.asc()
            )

    elif before:
        before_cursor = decode_cursor(before)
        beforeId = before_cursor["id"]
        beforeSortBy = before_cursor[sort_by] if sort_by in before_cursor else None

        if sort_by:
            if sort_order == "asc":
                query = filterFunc(
                    or_(
                        (orderAttr < beforeSortBy),
                        and_((orderAttr == beforeSortBy), (model.id < beforeId)),
                    )
                )
                query = query.order_by(orderAttr.desc(), model.id.desc())
            else:
                query = filterFunc(
                    or_(
                        (orderAttr > beforeSortBy),
                        and_((orderAttr == beforeSortBy), (model.id > beforeId)),
                    )
                )
                query = query.order_by(orderAttr.asc(), model.id.asc())

        else:
            query = filterFunc(model.id < beforeId)
            query = query.order_by(
                model.id.asc() if sort_order == "desc" else model.id.desc()
            )
    else:
        if sort_by:
            query = query.order_by(
                orderAttr.desc() if sort_order == "desc" else orderAttr.asc(),
                model.id.desc() if sort_order == "desc" else model.id.asc(),
            )
        else:
            query = query.order_by(model.id.asc())

    return query


def process_paged_result(result, limit, before, after, sort_by=None):
    hasMore = False
    if limit:
        hasMore = len(result) > limit

    if before:
        result = list(reversed(result))

    if hasMore:
        result = result[:-1]

    before_cursor_item = None
    after_cursor_item = None
    if result:
        before_cursor_item = (
            result[0]
            if ((before is not None and hasMore) or after is not None)
            else None
        )
        after_cursor_item = result[-1] if hasMore or before is not None else None

    before_cursor = (
        encode_cursor(
            before_cursor_item["id"],
            sort_by,
            before_cursor_item[sort_by] if sort_by else None,
        )
        if before_cursor_item
        else None
    )

    after_cursor = (
        encode_cursor(
            after_cursor_item["id"],
            sort_by,
            after_cursor_item[sort_by] if sort_by else None,
        )
        if after_cursor_item
        else None
    )

    # if result:
    #     idx = 0 if before is None else 1
    #     before_cursor = result[idx]['id'] if ((before is not None and hasMore) or after is not None)  else None
    #     if before:
    #         after_cursor = before
    #     elif (hasMore):
    #         after_cursor = result[-1]['id']

    return result, before_cursor, after_cursor


class AsyncRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.session = session
        self.model = model

    async def create_async(self, item: T, commit=True) -> T:
        self.session.add(item)
        if commit:
            await self.session.commit()
        return item

    async def upsert_async(self, item: T, commit=True) -> T:
        try:
            self.session.add(item)
            if commit:
                await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            await self.session.merge(item)
            if commit:
                await self.session.commit()
        return item

    async def get_async(
        self,
        item_id: int,
        tenant_id: Optional[int] = None,
        expand: Optional[List[str]] = None,
    ) -> T | None:
        query = select(self.model).filter(self.model.id == item_id)
        if tenant_id:
            query = query.filter(self.model.tenant_id == tenant_id)

        query = apply_joinedload(self.model, query, expand)

        query = query.limit(1)

        result = await self.session.execute(query)

        item = result.scalar_one_or_none()

        return item

    async def contains_intersect_async(
        self, tenant_id, ids: List[Any] = []
    ) -> List[Any]:
        query = select(self.model.id)
        if tenant_id:
            query = query.filter(self.model.tenant_id == tenant_id)

        query = query.filter(self.model.id.in_(ids))

        result = await self.session.execute(query)
        all = result.fetchall()

        return [item.id for item in all]

    async def find_one_async(
        self, *criterion: ColumnExpressionArgument[bool], expand: List[str] | None = None
    ) -> T | None:
        query = select(self.model)
        query = query.filter(*criterion)

        query = apply_joinedload(self.model, query, expand)

        query = query.limit(1)
        result = await self.session.execute(query)
        item = result.scalar_one_or_none()

        return item

    async def find_all_async(
        self, *criterion: ColumnExpressionArgument[bool], expand: List[str] | None = None
    ) -> Sequence[T]:
        query = select(self.model)
        if criterion:
            query = query.filter(*criterion)

        query = apply_joinedload(self.model, query, expand)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_async(
        self, tenant_id: int, *criterion: ColumnExpressionArgument[bool]
    ) -> int:
        query = select(func.count()).select_from(self.model)

        query = query.filter(self.model.tenant_id == tenant_id)
        if criterion:
            query = query.filter(*criterion)

        result = await self.session.execute(query)
        count = result.scalar_one()  # Extract the count
        return count

    async def _list_all_async(
        self,
        buildQuery: Callable[[], QueryT],
        buildOrderAttr: Callable[[], Column],
        limit: Optional[int] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        sort_by: Optional[list[str]] = None,
        sort_order: Optional[str] = None,
        expand: Optional[List[str]] = None,
    ):
        if before is not None and after is not None:
            raise ValueError(
                "Both 'before' and 'after' cannot be provided at the same time."
            )

        query = buildQuery()
        orderAttr = buildOrderAttr()

        query = apply_joinedload(self.model, query, expand)

        query = add_cursor_filter(
            self.model, query, after, before, sort_by, orderAttr, sort_order
        )

        if limit:
            query = query.limit(limit + 1)

        result = await self.session.execute(query)
        data = result.fetchall()
        column_names = result.keys()

        data = [dict(zip(column_names, row)) for row in data]
        # data = [item.to_dict() for item in data]

        data, before_cursor, after_cursor = process_paged_result(
            data, limit, before, after
        )

        return PagedResult(data, 0, before_cursor, after_cursor)

    async def update_async(self, item: T) -> T | None:
        await self.session.merge(item)
        await self.session.commit()
        updated_item = await self.session.get(self.model, item.id)

        if updated_item:
            await self.session.refresh(updated_item)

        return updated_item

    async def delete_async(self, tenant_id: int, item_id: int) -> None:
        item = await self.get_async(item_id, tenant_id)
        if item:
            await self.session.delete(item)
            await self.session.commit()
