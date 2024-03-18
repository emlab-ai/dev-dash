from datetime import datetime, timedelta

from sqlalchemy import func, and_, or_, cast, Float
from db.model import PullRequest
from db.model.pagedResult import PagedResult
from db.model.user import User
from sqlalchemy import func
import base64
import json

class PullRequestStats:
    def __init__(self, avg_loc, avg_duration, avg_files_changed, avg_comments_count):
        self.avg_loc = avg_loc
        self.avg_duration = avg_duration
        self.avg_files_changed = avg_files_changed
        self.avg_comments_count = avg_comments_count

class PullRequestsUsersStats:
    def __init__(self, authorId, count, avg_loc, sum_loc, max_loc, count_repos, avg_duration, max_duration):
        self.authorId = authorId
        self.count = count
        self.avg_loc = avg_loc
        self.sum_loc = sum_loc
        self.max_loc = max_loc
        self.count_repos = count_repos
        self.avg_duration = avg_duration
        self.max_duration = max_duration

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

def add_cursor_filter(query, after:str, before:str, sort_by:list[str], orderAttr, sort_order):
    if after:
        after_cursor = decode_cursor(after)
        afterId = after_cursor['id']
        afterSortBy = after_cursor[sort_by] if sort_by in after_cursor else None        

        if sort_by:
            if sort_order == 'asc':
                query = query.filter(or_((orderAttr > afterSortBy), and_((orderAttr == afterSortBy), (PullRequest.id > afterId))))
                query = query.order_by(orderAttr.asc(), PullRequest.id.asc())
            else:
                query = query.filter(or_((orderAttr < afterSortBy), and_((orderAttr == afterSortBy), (PullRequest.id < afterId))))
                query = query.order_by(orderAttr.desc(), PullRequest.id.desc())
        else:
            query = query.filter(PullRequest.id > afterId)
            query = query.order_by(PullRequest.id.desc() if sort_order == 'desc' else PullRequest.id.asc())

    elif before:
        query = query.filter(PullRequest.id < before)
        query = query.order_by(PullRequest.id.desc())
    else:
        if sort_by:
            query = query.order_by(orderAttr.desc() if sort_order == 'desc' else orderAttr.asc(), 
                                   PullRequest.id.desc() if sort_order == 'desc' else PullRequest.id.asc())
        else:
            query = query.order_by(PullRequest.id.asc())

    return query


class PullRequestRepository:
    def __init__(self, session):
        self.session = session

    def create(self, pr:PullRequest):
        try:
            self.session.add(pr)
            self.session.commit()
            return pr
        except Exception as error:
            print("Error while creating git_stats:", error)

    def get(self, id:int):
        try:
            git_stats = self.session.query(PullRequest).filter_by(id=id).first()
            return git_stats
        except Exception as error:
            print("Error while getting git_stats:", error)


    def list_all(self, start_date, end_date, users_ids:list[int] = None,  managers_ids:list[int] = None, limit:int = None, after=None, before=None, sort_by:str=None, sort_order:str=None) -> list[PullRequest]:
        try:
            if before is not None and after is not None:
                raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
            
            totalDurationFunc = cast(func.round(func.extract('epoch', PullRequest.closedAt-PullRequest.firstCommitDate) / 3600, 2), Float)
            changesFunc = PullRequest.additions + PullRequest.deletions
            orderAttr = None
            if sort_by and not hasattr(PullRequest, sort_by):
                if sort_by == 'totalDuration':
                    orderAttr = totalDurationFunc
                elif sort_by == 'changes':
                    orderAttr = changesFunc
                else:
                    raise ValueError(f"Invalid sort_by field: {sort_by}")
            elif sort_by:
                orderAttr = getattr(PullRequest, sort_by) 
            
            query = self.session.query(PullRequest)
            
            query = query.filter(func.date(PullRequest.closedAt) >= start_date.date(), func.date(PullRequest.closedAt) <= end_date.date())
            query = query.join(User, PullRequest.authorId == User.id)
            if(managers_ids is not None):
                query = query.filter(User.managerId.in_(managers_ids) | User.id.in_(managers_ids))
            
            if (users_ids is not None):
                query = query.filter(User.id.in_(users_ids))
            
            total_count = query.count()

            query = add_cursor_filter(query, after, before, sort_by, orderAttr, sort_order)
            
            if limit:
                query = query.limit(limit+1)

            query = query.with_entities(
                PullRequest.id, 
                PullRequest.author,
                PullRequest.authorId,
                PullRequest.prId,
                PullRequest.number,
                PullRequest.closedAt,
                PullRequest.createdAt,
                PullRequest.changedFiles,
                PullRequest.deletions,
                PullRequest.additions,
                PullRequest.bodyText,
                PullRequest.title,
                PullRequest.commitsCount,
                PullRequest.firstCommitMessage,
                PullRequest.firstCommitDate,
                PullRequest.repositoryName,
                PullRequest.repositoryUrl,
                PullRequest.reviewThreadsCount,
                PullRequest.resolvedCommentsCount,
                PullRequest.commentsCount,
                PullRequest.reactionsCount,
                PullRequest.url,
                (changesFunc).label('changes'),
                (totalDurationFunc).label('totalDuration'),
                User.name.label('author_name'))
            prs = query.all()
            prs = [item._asdict() for item in prs]
            
            hasMore = False
            if limit:
                hasMore = len(prs) > limit
                if (hasMore):
                    prs = prs[:-1]

            before_cursor = None
            after_cursor = None

            if before:
                prs = list(reversed(prs))

            if prs:
                before_cursor_item = prs[0] if ((before is not None and hasMore) or after is not None)  else None
                after_cursor_item = prs[-1] if hasMore or before is not None else None

            before_cursor = encode_cursor(before_cursor_item['id'], sort_by, before_cursor_item[sort_by] if sort_by else None) if before_cursor_item else None
            after_cursor = encode_cursor(after_cursor_item['id'], sort_by, after_cursor_item[sort_by] if sort_by else None) if after_cursor_item else None
           

            return PagedResult(prs, total_count, before_cursor, after_cursor)
        except Exception as error:
            print("Error while listing git_stats:", error)

    def get_pr_stats_group_by_user(self, start_date, end_date,  managerIds:list[int]) -> list[PullRequestsUsersStats]:
        try:
            query = self.session.query(PullRequest)
            query = query.filter(PullRequest.closedAt >= start_date, PullRequest.closedAt <= end_date)
            query = query.join(User, PullRequest.authorId == User.id)
            query = query.filter(User.managerId.in_(managerIds) | User.id.in_(managerIds))
            query = query.with_entities(PullRequest.authorId, func.count(PullRequest.id).label('count'), 
                                        func.avg(PullRequest.additions + PullRequest.deletions).label('avg_loc'), 
                                        func.sum(PullRequest.additions + PullRequest.deletions).label('sum_loc'), 
                                        func.max(PullRequest.additions + PullRequest.deletions).label('max_loc'), 
                                        func.count(PullRequest.repositoryName).label('count_repos'), 
                                        func.avg(PullRequest.closedAt-PullRequest.firstCommitDate).label('avg_duration'), 
                                        func.max(PullRequest.closedAt-PullRequest.firstCommitDate).label('max_duration')
                                        )
            query = query.group_by(PullRequest.authorId)

            prs_users_stats = query.all()

            return [item._asdict() for item in prs_users_stats]
        except Exception as error:
            print("Error while listing git_stats:", error)
    
    def get_avg_stats(self, start_date, end_date,  managerIds:list[int]) -> PullRequestStats:
        try:
           
            query = self.session.query(PullRequest)
            query = query.filter(PullRequest.closedAt >= start_date, PullRequest.closedAt <= end_date)
            query = query.join(User, PullRequest.authorId == User.id)
            query = query.filter(User.managerId.in_(managerIds) | User.id.in_(managerIds))

            query = query.with_entities(func.avg(PullRequest.additions + PullRequest.deletions).label('avg_loc'), 
                                        func.avg(PullRequest.changedFiles).label('avg_files_changed'), 
                                        func.avg(PullRequest.closedAt-PullRequest.firstCommitDate).label('avg_duration'), 
                                        func.avg(PullRequest.commentsCount).label('avg_comments_count'))

            prs = query.all()

            if prs[0].avg_loc is None:
                return PullRequestStats(0, 0, 0, 0)
            
            return PullRequestStats(round(prs[0].avg_loc, 2), 
                                    round(prs[0].avg_duration.total_seconds() / 3600, 2), 
                                    round(prs[0].avg_files_changed, 2), 
                                    round(prs[0].avg_comments_count, 2))
        except Exception as error:
            print("Error while listing git_stats:", error)

    def get_all_by_user(self, user_id:int, start_date:datetime, end_date:datetime,  limit:int = None, after=None, before=None, order_by:str=None) -> list[PullRequest]:
        try:
            if before is not None and after is not None:
                raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
            
            query = self.session.query(PullRequest)
            total_count = query.count()
            query = query.filter(PullRequest.closedAt >= start_date, PullRequest.closedAt <= end_date, PullRequest.authorId == user_id)
            
            if after:
                query = query.filter(PullRequest.id > after)
                query = query.order_by(PullRequest.id.asc())
            elif before:
                query = query.filter(PullRequest.id < before)
                query = query.order_by(PullRequest.id.desc())
            else:
                query = query.order_by(PullRequest.id.asc())
            
            if limit:
                query = query.limit(limit+1)

            prs = query.all()
            hasMore = False
            if limit:
                hasMore = len(prs) > limit
                if (hasMore):
                    prs = prs[:-1]

            before_cursor = None
            after_cursor = None

            if before:
                prs = list(reversed(prs))

            if prs:
                before_cursor = prs[0].id if ((before is not None and hasMore) or after is not None)  else None
                after_cursor = prs[-1].id if hasMore or before is not None else None

            return PagedResult(prs, total_count, before_cursor, after_cursor)
        except Exception as error:
            print("Error while listing git_stats:", error)

    def get_count_by_date_user(self, user_id:int, start_date:datetime, end_date:datetime):
        try:
            query = self.session.query(PullRequest)
            query = query.filter(PullRequest.closedAt >= start_date, PullRequest.closedAt <= end_date, PullRequest.authorId == user_id)
            query = query.with_entities(func.date_trunc('day', PullRequest.closedAt).label('closed_day'), 
                                        func.count(PullRequest.id).label('count')) 
            query = query.group_by(func.date_trunc('day', PullRequest.closedAt))

            prs = query.all()
            
            delta = end_date - start_date
            labels = [(start_date + timedelta(days=i)).date().isoformat() for i in range(delta.days + 1)]
            values = {item.closed_day.date().isoformat(): item.count for item in prs}

            data = [values.get(label, 0) for label in labels]

            return {
                "labels": labels,
                "data": data
            }
        except Exception as error:
            print("Error while listing git_stats:", error)
