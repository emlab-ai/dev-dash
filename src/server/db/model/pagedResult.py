from typing import Generic, List, Optional, TypeVar

T = TypeVar('T')

class PagedResult(Generic[T]):
    def __init__(self, data: List[T], total_count, before: Optional[str] = None, after: Optional[str] = None):
        self.data = data
        self.before = before
        self.after = after
        self.total_count = total_count
    
    def to_dict(self):
        return {
            'data': self.data,
            'before': self.before,
            'after': self.after,
            'totalCount': self.total_count
        }

