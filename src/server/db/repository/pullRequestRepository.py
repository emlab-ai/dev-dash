from datetime import datetime, timedelta
import pickle

from sqlalchemy import func, and_, or_, cast, Float
from db.model import PullRequest
from db.model.pagedResult import PagedResult
from db.model.user import User
from sqlalchemy import func
import base64
from db.model.githubUser import GithubUser
from db.repository.repository import add_cursor_filter
from db.model.githubRepo import GithubRepo

class PullRequestStats:
    def __init__(self, count, avg_loc, avg_duration, avg_files_changed, avg_comments_count):
        self.count = count
        self.avg_loc = avg_loc
        self.avg_duration = avg_duration
        self.avg_files_changed = avg_files_changed
        self.avg_comments_count = avg_comments_count

class PullRequestsUsersStats:
    def __init__(self, authorId, count, avg_loc, sum_loc, max_loc, count_repos, avg_duration, max_duration):
        self.author_id = authorId
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
        
    pickled_data = pickle.dumps(cursor)
    return base64.urlsafe_b64encode(pickled_data).decode('utf-8')

def decode_cursor(cursor: str) -> dict:
    decoded_string = base64.urlsafe_b64decode(cursor)
    return pickle.loads(decoded_string)

class PullRequestRepository:
    def __init__(self, session):
        self.session = session

    def create(self, pr:PullRequest):
        self.session.add(pr)
        self.session.commit()
        return pr

    def get(self, id:int):
        git_stats = self.session.query(PullRequest).filter_by(id=id).first()
        return git_stats

    def list_all(self, tenant_id:int, start_date, end_date, github_users_ids:list[int] = None, limit:int = None, after=None, before=None, sort_by:str=None, sort_order:str=None) -> list[PullRequest]:
        if before is not None and after is not None:
            raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
        
        totalDurationFunc = cast(func.round(func.extract('epoch', PullRequest.closed_at-PullRequest.first_commit_date) / 3600, 2), Float)
        changesFunc = PullRequest.additions + PullRequest.deletions
        
        sorting_keys = {
            "id": {
                "id":"id",
                "attr": PullRequest.id
                },
            "closed_at": {
                "id":"closed_at",
                "attr": PullRequest.closed_at
            },
            "totalDuration": {
                "id":"total_duration",
                "attr": totalDurationFunc
                },
            "changes": {
                "id":"changes",
                "attr": changesFunc
            },
            "changedFiles":{
                "id":"changed_files",
                "attr": PullRequest.changed_files
            },
            "reviewThreadsCount":{
                "id":"review_threads_count",
                "attr": PullRequest.review_threads_count
            },
            "reviewThreadsCount": {
                "id":"review_threads_count",
                "attr": PullRequest.review_threads_count
            },
            "commentsCount":{
                "id":"comments_count",
                "attr": PullRequest.comments_count
            }
        }
        
        if sort_by and (not sort_by in sorting_keys):
            raise ValueError(f"Invalid sort_by field: {sort_by}")
        
        if sort_by:
            sorting_data = sorting_keys[sort_by]
        else: 
            sorting_data = sorting_keys["id"]
            
        query = self.session.query(PullRequest)
        query = query.filter(PullRequest.tenant_id == tenant_id)
        
        query = query.filter(func.date(PullRequest.closed_at) >= start_date.date(), func.date(PullRequest.closed_at) <= end_date.date())
        query = query.join(GithubUser, PullRequest.author_id == GithubUser.id)
        
        if (github_users_ids is not None):
            query = query.filter(GithubUser.id.in_(github_users_ids))
        
        total_count = query.count()

        query = add_cursor_filter(PullRequest, query, after, before, sort_by, sorting_data["attr"], sort_order, group = False)
        
        if limit:
            query = query.limit(limit+1)

        query = query.with_entities(
            PullRequest.id, 
            PullRequest.author,
            PullRequest.author_id,
            PullRequest.node_id,
            PullRequest.number,
            PullRequest.closed_at,
            PullRequest.created_at,
            PullRequest.changed_files,
            PullRequest.deletions,
            PullRequest.additions,
            PullRequest.body,
            PullRequest.title,
            PullRequest.commits_count,
            PullRequest.first_commit_message,
            PullRequest.first_commit_date,
            PullRequest.review_threads_count,
            PullRequest.comments_count,
            PullRequest.url,
            (changesFunc).label('changes'),
            (totalDurationFunc).label('total_duration'))

        prs = query.all()
        prs = [item._asdict() for item in prs]
        
        hasMore = False
        if limit:
            hasMore = len(prs) > limit
            if (hasMore):
                prs = prs[:-1]

        before_cursor_item = None
        after_cursor_item = None

        if before:
            prs = list(reversed(prs))

        if prs:
            before_cursor_item = prs[0] if ((before is not None and hasMore) or after is not None)  else None
            after_cursor_item = prs[-1] if hasMore or before is not None else None
            
        sort_by_key = None
        if sort_by:
            sort_by_key = sorting_data["id"]

        before_cursor = encode_cursor(before_cursor_item['id'], sort_by, before_cursor_item[sort_by_key] if sort_by_key else None) if before_cursor_item else None
        after_cursor = encode_cursor(after_cursor_item['id'], sort_by, after_cursor_item[sort_by_key] if sort_by_key else None) if after_cursor_item else None

        return PagedResult(prs, total_count, before_cursor, after_cursor)

    def get_pr_stats_group_by_user(self, tenant_id:int, start_date, end_date,  github_user_ids:list[int], limit:int = None, after=None, before=None, sort_by:str=None, sort_order:str=None) -> PagedResult[PullRequestsUsersStats]:
        countFunc = func.coalesce(func.count(PullRequest.id), 0)
        avgLocFunc = func.avg(func.coalesce(PullRequest.additions, 0) + func.coalesce(PullRequest.deletions, 0))
        sumLocFunc = func.sum(func.coalesce(PullRequest.additions, 0) + func.coalesce(PullRequest.deletions, 0))
        maxLocFunc = func.max(func.coalesce(PullRequest.additions, 0) + func.coalesce(PullRequest.deletions, 0))
        avgDurationFunc = func.avg(func.coalesce(PullRequest.closed_at, func.current_date())-func.coalesce(PullRequest.first_commit_date, func.current_date()))
        maxDurationFunc = func.max(func.coalesce(PullRequest.closed_at, func.current_date())-func.coalesce(PullRequest.first_commit_date, func.current_date()))
        
        sorting_keys = {
            "id": {
                "id":"id",
                "attr": GithubUser.id
                },
            "name": {
                "id":"user_name",
                "attr": User.name
            },
            "count": {
                "id":"count",
                "attr": countFunc
                },
            "avg_loc": {
                "id":"avg_loc",
                "attr": avgLocFunc
            },
            "sum_loc":{
                "id":"sum_loc",
                "attr": sumLocFunc
            },
            "max_loc":{
                "id":"max_loc",
                "attr": maxLocFunc
            },
            "avg_duration": {
                "id":"avg_duration",
                "attr": avgDurationFunc
            },
            "max_duration":{
                "id":"max_duration",
                "attr": maxDurationFunc
            }
        }
        
        if sort_by and (not sort_by in sorting_keys):
            raise ValueError(f"Invalid sort_by field: {sort_by}")
        
        if sort_by:
            sorting_data = sorting_keys[sort_by]
        else: 
            sorting_data = sorting_keys["id"]
        
        query = self.session.query(GithubUser)        
        query = query.outerjoin(PullRequest, 
                                and_(
                                    PullRequest.author_id == GithubUser.id,
                                    PullRequest.tenant_id == tenant_id, 
                                    PullRequest.closed_at >= start_date, 
                                    PullRequest.closed_at <= end_date))
        query = query.outerjoin(User, GithubUser.id == User.github_user_id)
        query = query.filter(GithubUser.tenant_id == tenant_id)
        
        if github_user_ids:
            query = query.filter(GithubUser.id.in_(github_user_ids))
                    
        query = add_cursor_filter(GithubUser, query, after, before, sort_by, sorting_data["attr"], sort_order, group=True)    
            
        query = query.with_entities(
            GithubUser.login.label('github_login'),
            GithubUser.id, 
            User.name.label('user_name'),
            User.id.label('user_id'),            
            countFunc.label('count'), 
            avgLocFunc.label('avg_loc'), 
            sumLocFunc.label('sum_loc'), 
            maxLocFunc.label('max_loc'), 
            avgDurationFunc.label('avg_duration'), 
            maxDurationFunc.label('max_duration'))
        
        query = query.group_by(GithubUser.login, GithubUser.id, User.name, User.id)
        
        if limit:   
            query = query.limit(limit+1)

        prs = query.all()

        prs = [item._asdict() for item in prs]
    
        hasMore = False
        if limit:
            hasMore = len(prs) > limit
            if (hasMore):
                prs = prs[:-1]

        before_cursor_item = None
        after_cursor_item = None

        if before:
            prs = list(reversed(prs))

        if prs:
            before_cursor_item = prs[0] if ((before is not None and hasMore) or after is not None)  else None
            after_cursor_item = prs[-1] if hasMore or before is not None else None

        sort_by_key = None
        if sort_by:
            sort_by_key = sorting_data["id"]

        before_cursor = encode_cursor(before_cursor_item['id'], sort_by, before_cursor_item[sort_by_key] if sort_by_key else None) if before_cursor_item else None
        after_cursor = encode_cursor(after_cursor_item['id'], sort_by, after_cursor_item[sort_by_key] if sort_by_key else None) if after_cursor_item else None

        return PagedResult(prs, 0, before_cursor, after_cursor)
    
    def get_pr_stats_group_by_repo(self, tenant_id:int, start_date, end_date,  github_user_ids:list[int], limit:int = None, after=None, before=None, sort_by:str=None, sort_order:str=None) -> PagedResult[PullRequestsUsersStats]:
        countFunc = func.coalesce(func.count(PullRequest.id), 0)
        avgLocFunc = func.avg(func.coalesce(PullRequest.additions, 0) + func.coalesce(PullRequest.deletions, 0))
        sumLocFunc = func.sum(func.coalesce(PullRequest.additions, 0) + func.coalesce(PullRequest.deletions, 0))
        maxLocFunc = func.max(func.coalesce(PullRequest.additions, 0) + func.coalesce(PullRequest.deletions, 0))
        avgDurationFunc = func.avg(func.coalesce(PullRequest.closed_at, func.current_date())-func.coalesce(PullRequest.first_commit_date, func.current_date()))
        maxDurationFunc = func.max(func.coalesce(PullRequest.closed_at, func.current_date())-func.coalesce(PullRequest.first_commit_date, func.current_date()))
        
        sorting_keys = {
            "id": {
                "id":"id",
                "attr": GithubRepo.id
                },
            "name": {
                "id":"name",
                "attr": GithubRepo.name
            },
            "count": {
                "id":"count",
                "attr": countFunc
                },
            "avg_loc": {
                "id":"avg_loc",
                "attr": avgLocFunc
            },
            "sum_loc":{
                "id":"sum_loc",
                "attr": sumLocFunc
            },
            "max_loc":{
                "id":"max_loc",
                "attr": maxLocFunc
            },
            "avg_duration": {
                "id":"avg_duration",
                "attr": avgDurationFunc
            },
            "max_duration":{
                "id":"max_duration",
                "attr": maxDurationFunc
            }
        }
        
        if sort_by and (not sort_by in sorting_keys):
            raise ValueError(f"Invalid sort_by field: {sort_by}")
        
        if sort_by:
            sorting_data = sorting_keys[sort_by]
        else: 
            sorting_data = sorting_keys["id"]
        
        query = self.session.query(GithubRepo)        
        query = query.outerjoin(PullRequest, 
                                and_(
                                    PullRequest.repository_id == GithubRepo.id,
                                    PullRequest.tenant_id == tenant_id, 
                                    PullRequest.closed_at >= start_date, 
                                    PullRequest.closed_at <= end_date))
        query = query.filter(GithubRepo.tenant_id == tenant_id)
        
        if github_user_ids:
            query = query.filter(PullRequest.author_id.in_(github_user_ids))
                    
        query = add_cursor_filter(GithubRepo, query, after, before, sort_by, sorting_data["attr"], sort_order, group=True)    
            
        query = query.with_entities(
            GithubRepo.id,             
            GithubRepo.name.label('name'),              
            countFunc.label('count'), 
            avgLocFunc.label('avg_loc'), 
            sumLocFunc.label('sum_loc'), 
            maxLocFunc.label('max_loc'), 
            avgDurationFunc.label('avg_duration'), 
            maxDurationFunc.label('max_duration'))
        
        query = query.group_by(GithubRepo.id, GithubRepo.name)
        
        if limit:   
            query = query.limit(limit+1)

        prs = query.all()

        prs = [item._asdict() for item in prs]
    
        hasMore = False
        if limit:
            hasMore = len(prs) > limit
            if (hasMore):
                prs = prs[:-1]

        before_cursor_item = None
        after_cursor_item = None

        if before:
            prs = list(reversed(prs))

        if prs:
            before_cursor_item = prs[0] if ((before is not None and hasMore) or after is not None)  else None
            after_cursor_item = prs[-1] if hasMore or before is not None else None

        sort_by_key = None
        if sort_by:
            sort_by_key = sorting_data["id"]

        before_cursor = encode_cursor(before_cursor_item['id'], sort_by, before_cursor_item[sort_by_key] if sort_by_key else None) if before_cursor_item else None
        after_cursor = encode_cursor(after_cursor_item['id'], sort_by, after_cursor_item[sort_by_key] if sort_by_key else None) if after_cursor_item else None

        return PagedResult(prs, 0, before_cursor, after_cursor)
    
    
    def get_avg_stats(self, tenant_id:int, start_date, end_date, github_user_ids:list[int]) -> PullRequestStats:
        query = self.session.query(PullRequest)
        query = query.filter(PullRequest.tenant_id == tenant_id)
        query = query.filter(PullRequest.closed_at >= start_date, PullRequest.closed_at <= end_date)
        
        if github_user_ids:
            query = query.filter(PullRequest.author_id.in_(github_user_ids))

        query = query.with_entities(
            func.count(PullRequest.id).label('count'),
            func.avg(PullRequest.additions + PullRequest.deletions).label('avg_loc'), 
            func.avg(PullRequest.changed_files).label('avg_files_changed'), 
            func.avg(PullRequest.closed_at-PullRequest.first_commit_date).label('avg_duration'), 
            func.avg(PullRequest.comments_count).label('avg_comments_count'))

        prs = query.all()

        if prs[0].avg_loc is None:
            return PullRequestStats(0, 0, 0, 0, 0)
        
        return PullRequestStats(
            prs[0].count,
            round(prs[0].avg_loc, 2), 
            round(prs[0].avg_duration.total_seconds() / 3600, 2), 
            round(prs[0].avg_files_changed, 2), 
            round(prs[0].avg_comments_count, 2))

    def get_all_by_user(self, tenant_id:int, user_id:int, start_date:datetime, end_date:datetime,  limit:int = None, after=None, before=None, order_by:str=None) -> list[PullRequest]:
        if before is not None and after is not None:
            raise ValueError("Both 'before' and 'after' cannot be provided at the same time.")
        
        query = self.session.query(PullRequest)
        query = query.filter(PullRequest.tenant_id == tenant_id)
        total_count = query.count()
        query = query.filter(PullRequest.closed_at >= start_date, PullRequest.closed_at <= end_date, PullRequest.author_id == user_id)
        
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

    def get_count_by_date_user(self, tenant_id:int, github_user_id:int, start_date:datetime, end_date:datetime):
        query = self.session.query(PullRequest)
        query = query.filter(PullRequest.tenant_id == tenant_id)
        query = query.filter(PullRequest.closed_at >= start_date, PullRequest.closed_at <= end_date, PullRequest.author_id == github_user_id)
        query = query.with_entities(func.date_trunc('day', PullRequest.closed_at).label('closed_day'), 
                                    func.count(PullRequest.id).label('count')) 
        query = query.group_by(func.date_trunc('day', PullRequest.closed_at))

        prs = query.all()
        
        delta = end_date - start_date
        labels = [(start_date + timedelta(days=i)).date().isoformat() for i in range(delta.days + 1)]
        values = {item.closed_day.date().isoformat(): item.count for item in prs}

        data = [values.get(label, 0) for label in labels]

        return {
            "labels": labels,
            "data": data
        }
