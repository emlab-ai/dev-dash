import base64
import json
from typing import Callable, Generic, List, Type, TypeVar
from sqlalchemy import ColumnExpressionArgument, and_, or_
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import IntegrityError
from db.model.pagedResult import PagedResult, process_paged_result

T = TypeVar('T')

def encode_cursor(id, sort_by: str, sort_by_value) -> str:
    cursor = {
        "id": id        
    }
    if sort_by:
        cursor[sort_by] = sort_by_value
    return base64.b64encode(json.dumps(cursor).encode('utf-8')).decode('utf-8')

def decode_cursor(cursor: str) -> dict:
    decoded_string = base64.b64decode(cursor).decode('utf-8')
    return json.loads(decoded_string)

def add_cursor_filter(model:T, query, after:str, before:str, sort_by:list[str], orderAttr, sort_order):
    if after:
        after_cursor = decode_cursor(after)
        afterId = after_cursor['id']
        afterSortBy = after_cursor[sort_by] if sort_by in after_cursor else None        

        if sort_by:
            if sort_order == 'asc':
                query = query.filter(or_((orderAttr > afterSortBy), and_((orderAttr == afterSortBy), (model.id > afterId))))
                query = query.order_by(orderAttr.asc(), model.id.asc())
            else:
                query = query.filter(or_((orderAttr < afterSortBy), and_((orderAttr == afterSortBy), (model.id < afterId))))
                query = query.order_by(orderAttr.desc(), model.id.desc())
        else:
            query = query.filter(model.id > afterId)
            query = query.order_by(model.id.desc() if sort_order == 'desc' else model.id.asc())

    elif before:
        query = query.filter(model.id < before)
        query = query.order_by(model.id.desc())
    else:
        if sort_by:
            query = query.order_by(orderAttr.desc() if sort_order == 'desc' else orderAttr.asc(), 
                                   model.id.desc() if sort_order == 'desc' else model.id.asc())
        else:
            query = query.order_by(model.id.asc())

    return query


class Repository(Generic[T]):
    def __init__(self, model:Type[T], session:Session):
        self.session = session
        self.model = model

    def create(self, item:T, commit=True) -> T:
        self.session.add(item)
        if commit: self.session.commit() 
        return item

    def upsert(self, item:T, commit=True) -> T:
        try:
            self.session.add(item)
            if commit: 
                self.session.commit()
        except IntegrityError:
            self.session.rollback()
            self.session.merge(item)
            if commit: 
                self.session.commit()
        return item

    def get(self, item_id:int, tenant_id: int = None) -> T:
        query = self.session.query(self.model).filter(self.model.id == item_id)
        if (tenant_id):
            query = query.filter(self.model.tenant_id == tenant_id)

        item = query.first()
        return item
    
    def find_one(self, *criterion: ColumnExpressionArgument[bool]) -> T:
        query = self.session.query(self.model)
        query = query.filter(*criterion)
        item = query.first()
        return item
    
    def find_all(self, *criterion: ColumnExpressionArgument[bool])-> List[T]:
        query = self.session.query(self.model)
        if (criterion):
            query = query.filter(*criterion)
        result = query.all()
        return result
    
    def count(self, *criterion: ColumnExpressionArgument[bool]) -> int:
        query = self.session.query(self.model)
        if (criterion):
            query = query.filter(*criterion)
        return query.count()

    def _list_all(self, buildQuery: Callable[[Query[any]], Query[any]], builOrderAttr:Callable[[], any], limit=None, after=None, before=None, sort_by:str=None, sort_order:str=None):
        if before is not None and after is not None:
            raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
        
        query = self.session.query(self.model)
        total_count = query.count()
        
        query = buildQuery(query)
        orderAttr = builOrderAttr()

        query = add_cursor_filter[T](self.model, query, after, before, sort_by, orderAttr, sort_order)
            
        result = query.all()

        result = [item.to_dict() for item in result]
        
        result, before_cursor, after_cursor = process_paged_result(result, limit, before, after)

        return PagedResult(result, total_count, before_cursor, after_cursor)

    def update(self, item:T)->T:
        self.session.merge(item)
        self.session.commit()
        return item

    def delete(self, item_id:int)->None:
        item = self.session.query(self.model).filter(self.model.id==item_id).first()
        self.session.delete(item)
        self.session.commit()