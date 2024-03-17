from typing import Generic, List, Optional, TypeVar

T = TypeVar('T')

class PagedResult(Generic[T]):
    def __init__(self, data: List[T], total_count, before: Optional[str] = None, after: Optional[str] = None):
        self.data = data
        self.before = before
        self.after = after
        self.total_count = total_count

def process_paged_result(result, limit, before, after):
    hasMore = False
    if limit:
        hasMore = len(result) > limit

    before_cursor = None
    after_cursor = None

    if before:
        result = list(reversed(result))

    if result:
        idx = 0 if before is None else 1
        before_cursor = result[idx]['id'] if ((before is not None and hasMore) or after is not None)  else None
        if before:
            after_cursor = before
        elif (hasMore): 
            after_cursor = result[-1]['id']

    if hasMore:
        result = result[:-1]

    return result, before_cursor, after_cursor