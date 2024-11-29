import base64
import json
import pickle
from typing import Any, Callable, Generic, List, Type, TypeVar
from sqlalchemy import ColumnExpressionArgument, and_, or_
from sqlalchemy.orm import Session, Query, joinedload
from sqlalchemy.exc import IntegrityError
from db.model.pagedResult import PagedResult

T = TypeVar('T')

def encode_cursor(id, sort_by: str, sort_by_value) -> str:
    cursor = {
        "id": id        
    }
    if sort_by:
        cursor[sort_by] = sort_by_value
        
    pickled_data = pickle.dumps(cursor)
    return base64.urlsafe_b64encode(pickled_data).decode('utf-8')

def decode_cursor(cursor: str) -> dict:
    decoded_string = base64.urlsafe_b64decode(cursor)
    return pickle.loads(decoded_string)

def apply_joinedload(model, query: Query, expand: List[str]) -> Query:
    if expand:
        for expandedProp in expand:
            query = query.options(joinedload(getattr(model, expandedProp)))
    return query

def add_cursor_filter(model:T, query, after:str, before:str, sort_by:list[str], orderAttr, sort_order, group:bool=False):
    
    filterFunc = query.having if group else query.filter
    if after:
        after_cursor = decode_cursor(after)
        afterId = after_cursor['id']
        afterSortBy = after_cursor[sort_by] if sort_by in after_cursor else None                        

        if sort_by:
            if sort_order == 'asc':
                query = filterFunc(or_((orderAttr > afterSortBy), and_((orderAttr == afterSortBy), (model.id > afterId))))
                query = query.order_by(orderAttr.asc(), model.id.asc())
            else:
                query = filterFunc(or_((orderAttr < afterSortBy), and_((orderAttr == afterSortBy), (model.id < afterId))))
                query = query.order_by(orderAttr.desc(), model.id.desc())
        else:
            query = filterFunc(model.id > afterId)
            query = query.order_by(model.id.desc() if sort_order == 'desc' else model.id.asc())

    elif before:
        before_cursor = decode_cursor(before)
        beforeId = before_cursor['id']
        beforeSortBy = before_cursor[sort_by] if sort_by in before_cursor else None      
        
        if sort_by:
            if sort_order == 'asc':
                query = filterFunc(or_((orderAttr < beforeSortBy), and_((orderAttr == beforeSortBy), (model.id < beforeId))))
                query = query.order_by(orderAttr.desc(), model.id.desc())
            else:
                query = filterFunc(or_((orderAttr > beforeSortBy), and_((orderAttr == beforeSortBy), (model.id > beforeId))))
                query = query.order_by(orderAttr.asc(), model.id.asc())

        else:
            query = filterFunc(model.id < beforeId)
            query = query.order_by(model.id.asc() if sort_order == 'desc' else model.id.desc())
    else:
        if sort_by:
            query = query.order_by(orderAttr.desc() if sort_order == 'desc' else orderAttr.asc(), 
                                   model.id.desc() if sort_order == 'desc' else model.id.asc())
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
        before_cursor_item = result[0] if ((before is not None and hasMore) or after is not None)  else None
        after_cursor_item = result[-1] if hasMore or before is not None else None

    before_cursor = encode_cursor(before_cursor_item['id'], sort_by, before_cursor_item[sort_by] if sort_by else None) if before_cursor_item else None
    after_cursor = encode_cursor(after_cursor_item['id'], sort_by, after_cursor_item[sort_by] if sort_by else None) if after_cursor_item else None


    # if result:
    #     idx = 0 if before is None else 1
    #     before_cursor = result[idx]['id'] if ((before is not None and hasMore) or after is not None)  else None
    #     if before:
    #         after_cursor = before
    #     elif (hasMore): 
    #         after_cursor = result[-1]['id']


        

    return result, before_cursor, after_cursor


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

    def get(self, item_id:int, tenant_id: int = None, expand:List[str]=None) -> T:
        query = self.session.query(self.model).filter(self.model.id == item_id)
        if (tenant_id):
            query = query.filter(self.model.tenant_id == tenant_id)
            
        query = apply_joinedload(self.model, query, expand)

        item = query.first()
        return item
    
    def contains_intersect(self, tenant_id, ids:List[Any]=[]) -> List[Any]:
        query = self.session.query(self.model)
        if (tenant_id):
            query = query.filter(self.model.tenant_id == tenant_id)

        query = query.filter(self.model.id.in_(ids))
        query = query.with_entities(self.model.id)
            
        result = query.all()
        
        return [item.id for item in result]
    
    def find_one(self, *criterion: ColumnExpressionArgument[bool], expand:List[str]=None) -> T:
        query = self.session.query(self.model)
        query = query.filter(*criterion)
        

        query = apply_joinedload(self.model, query, expand)
                
        item = query.first()
        return item
    
    def find_all(self, *criterion: ColumnExpressionArgument[bool], expand:List[str]=None)-> List[T]:
        query = self.session.query(self.model)
        if (criterion):
            query = query.filter(*criterion)
        
        query = apply_joinedload(self.model, query, expand)
            
        result = query.all()
        return result
    
    def count(self, tenant_id:int, *criterion: ColumnExpressionArgument[bool]) -> int:
        query = self.session.query(self.model)
        query = query.filter(self.model.tenant_id == tenant_id)
        if (criterion):
            query = query.filter(*criterion)
        return query.count()

    def _list_all(self, buildQuery: Callable[[Query[any]], Query[any]], builOrderAttr:Callable[[], any], limit=None, after=None, before=None, sort_by:str=None, sort_order:str=None, expand:List[str]=None):
        if before is not None and after is not None:
            raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
        
        query = self.session.query(self.model)
        total_count = query.count()
        
        query = buildQuery(query)
        orderAttr = builOrderAttr()
        
        query = apply_joinedload(self.model, query, expand)

        query = add_cursor_filter[T](self.model, query, after, before, sort_by, orderAttr, sort_order)
        
        if limit:
            query = query.limit(limit+1)
            
        result = query.all()

        result = [item.to_dict() for item in result]
        
        result, before_cursor, after_cursor = process_paged_result(result, limit, before, after)

        return PagedResult(result, total_count, before_cursor, after_cursor)

    def update(self, item:T)->T:
        self.session.merge(item)
        self.session.commit()
        item = self.session.query(self.model).get(item.id)
        self.session.refresh(item)
        return item

    def delete(self, item_id:int)->None:
        item = self.session.query(self.model).filter(self.model.id==item_id).first()
        self.session.delete(item)
        self.session.commit()