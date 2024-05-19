import datetime
from statistics import quantiles
from typing import List

from numpy import mean
from db.repository import PullRequestRepository
from services.userService import UsersService


percent_difference = lambda a, b: round(((a - b) / b), 2) if b > 0 else 0


def duration_to_hours(duration):
    if duration is None:
        return 0
    
    return round(duration.total_seconds() / 3600, 2)

class StatsService:
    def __init__(self, session):
        self.session = session
    
    def build_cues(self, tenant_id:int, managerId:int, start_date:datetime, end_date:datetime):
        prRepository = PullRequestRepository(self.session)
        userService = UsersService(self.session)
        
        user_ids = None
        if managerId is not None:
            manager_ids = userService.get_manager_chain(tenant_id, managerId)
            user_ids = userService.get_github_user_for_manager_ids(tenant_id, manager_ids)
            
        if managerId is not None:
            reports = userService.get_all_reports(tenant_id, managerId, directOnly=False)
            total_swes = len(reports)
            total_swes_prev = len(reports)
        else:
            total_swes = None
            total_swes_prev = None

        difference = end_date - start_date 
        start_date_prev = start_date - difference 
        end_date_prev = start_date
        
        result = prRepository.list_all(tenant_id, start_date, end_date, github_users_ids=user_ids)
        result_prev = prRepository.list_all(tenant_id, start_date_prev, end_date_prev, github_users_ids=user_ids)

        result = result.data if result else []
        result_prev = result_prev.data if result_prev else []

        unique_swes = len(set([pr["author_id"] for pr in result]))
        unique_swes_prev = len(set([pr["author_id"] for pr in result_prev]))
        
        if not total_swes:
            total_swes = unique_swes
            total_swes_prev = unique_swes_prev

        diffLess100 = len([pr for pr in result if pr["deletions"]+pr["additions"] <= 100])
        diffLess100_prev = len([pr for pr in result_prev if pr["deletions"]+pr["additions"] <= 100])

        return [
                {
                    "label": 'SWE count',
                    "id": 'sweCount',
                    "value": total_swes,
                    "diffPercent": percent_difference(total_swes_prev, total_swes)
                },
                {
                    "label": 'PRs count',
                    "id": 'diffCount',
                    "value": len(result),
                    "diffPercent": percent_difference(len(result_prev), len(result))
                },
                {
                    "label": 'PRs per SWE',
                    "id": 'diffPerSwe',
                    "value": round((len(result) / total_swes) if total_swes > 0 else 0, 2),
                    "diffPercent": percent_difference(round((len(result_prev) / total_swes_prev) if total_swes_prev > 0 else 0, 2), round((len(result) / total_swes) if total_swes > 0 else 0, 2))
                },
                {
                    "label": 'Active SWEs',
                    "id": 'activeSwe',
                    "value": unique_swes,
                    "diffPercent": percent_difference(unique_swes_prev, unique_swes)
                },
                {
                    "label": '% of PRs <= 100 LoC',
                    "id": 'diffLess100',
                    "value": diffLess100,
                    "diffPercent": percent_difference(diffLess100_prev, diffLess100)
                }
            ]

    def build_line_charts(self, tenant_id:int, managerId:int, start_date:datetime, end_date:datetime):
        date_range = [(start_date + datetime.timedelta(days=i)).date() for i in range((end_date - start_date).days + 1)]

        prRepository = PullRequestRepository(self.session)
        userService = UsersService(self.session)
        total_swes = None
        
        github_user_ids = None
        
        if managerId is not None:
            managerIds = userService.get_manager_chain(tenant_id, managerId)
            github_user_ids = userService.get_github_user_for_manager_ids(tenant_id, managerIds)
            reports = userService.get_all_reports(tenant_id, managerId, directOnly=False)
            total_swes = len(reports)      

        result = prRepository.list_all(tenant_id, start_date, end_date, github_user_ids)
        result = result.data if result else []
        unique_swes = len(set([pr["author_id"] for pr in result]))
        
        if not total_swes:
            total_swes = unique_swes
                    
        grouped_by_date = {}
        less100_grouped_by_date = {}
        active_swe_by_date = {}
        for pr in result:
            closed_date = pr["closed_at"].date()
            if closed_date not in grouped_by_date:
                grouped_by_date[closed_date] = 0
                less100_grouped_by_date[closed_date] = 0
                active_swe_by_date[closed_date] = set()
            grouped_by_date[closed_date] += 1   
            less100_grouped_by_date[closed_date] += 1 if pr["deletions"]+pr["additions"] <= 100 else 0
            active_swe_by_date[closed_date].add(pr["author_id"]) 

        # Calculate average total_duration_h per day
        average_duration_per_day = {}
        for pr in result:
            closed_date = pr["closed_at"].date()
            if closed_date not in average_duration_per_day:
                average_duration_per_day[closed_date] = []
            
            average_duration_per_day[closed_date].append(pr["total_duration"])

        p80_duration_per_day = {}
        for date, durations in average_duration_per_day.items():
            average_duration_per_day[date] = mean(durations)
            if len(durations) < 2:
                p80_duration_per_day[date] = 0
            else:
                p80_duration_per_day[date] = quantiles(durations, n=100)[80]

        labels = date_range#[date.strftime('%Y-%m-%d') for date in date_range]

        return [
            {
                "id": 'diffsPerDay',
                "title": 'Diffs per day',
                "labels": labels,
                "datasets": [
                    {
                        "label": 'Diffs Per SWE',
                        "data": [grouped_by_date.get(date, 0) / total_swes for date in date_range]
                    },
                    {
                        "label": 'Diffs Per Active SWE',
                        "data": [(grouped_by_date.get(date, 0) / unique_swes) if unique_swes>0 else 0 for date in date_range]
                    }
                ]
            },
            {
                "id": 'diffSweCount',
                "title": 'SWE and PRs Count',
                "labels": labels,
                "datasets": [
                    {
                        "label": 'PRs Count',
                        "data": [grouped_by_date.get(date, 0) for date in date_range]
                    },
                    {
                        "label": 'Active SWE Count',
                        "data": [len(active_swe_by_date.get(date, set())) for date in date_range]
                    }
                    ,
                    {
                        "label": 'SWE Count',
                        "data": [total_swes for date in date_range]
                    }
                ]
            },
            {
                "id": 'timePerDiff',
                "title": 'Average time to close',
                "labels": labels,
                "datasets": [
                    {
                        "label": 'Average: First commit to close',
                        "data": [average_duration_per_day.get(date, 0) for date in date_range]
                    },
                    {
                        "label": 'P80: First commit to close',
                        "data": [p80_duration_per_day.get(date, 0) for date in date_range]
                    }
                ]
            },
            {
                "id": 'activeSWEs',
                "title": '% Active SWEs',
                "labels": labels,
                "datasets": [
                    {
                        "label": 'Active SWEs',
                        "data": [round(len(active_swe_by_date.get(date, []))/total_swes, 2) for date in date_range]
                    }
                ]
            },
            {
                "id": 'smallDiffs',
                "title": '% Diffs less than 100 LoC',
                "labels": labels,
                "datasets": [
                    {
                        "label": 'Diffs <= 100 LoC',
                        "data": [less100_grouped_by_date.get(date, 0) / grouped_by_date.get(date, 1) for date in date_range]
                    }
                ]
            }
        ]
    
    def build_user_stats(self, tenant_id:int, github_user_ids:List[int], start_date, end_date, limit=None, after=None, before=None, sort_by=None, sort_order=None):
        prRepository = PullRequestRepository(self.session)

        result = prRepository.get_pr_stats_group_by_user(tenant_id, start_date, end_date, github_user_ids, limit, after, before, sort_by, sort_order)

        for item in result.data:
            item["avg_duration"] = duration_to_hours(item["avg_duration"])
            item["max_duration"] = duration_to_hours(item["max_duration"]) 
            item["avg_loc"] = round(item["avg_loc"], 2) if item["avg_loc"] else 0


        return result.to_dict()
    
    def build_repo_stats(self, tenant_id:int, github_user_ids:List[int], start_date, end_date, limit=None, after=None, before=None, sort_by=None, sort_order=None):
        prRepository = PullRequestRepository(self.session)

        result = prRepository.get_pr_stats_group_by_repo(tenant_id, start_date, end_date, github_user_ids, limit, after, before, sort_by, sort_order)

        for item in result.data:
            item["avg_duration"] = duration_to_hours(item["avg_duration"])
            item["max_duration"] = duration_to_hours(item["max_duration"]) 
            item["avg_loc"] = round(item["avg_loc"], 2) if item["avg_loc"] else 0


        return result.to_dict()