import datetime
from statistics import quantiles

from numpy import mean
from db.repository import PullRequestRepository
from services.userService import UsersService


percent_difference = lambda a, b: round(((a - b) / b), 2) if b > 0 else 0

class StatsService:
    def __init__(self, session):
        self.session = session
    
    def build_cues(self, managerId:int, start_date:datetime, end_date:datetime):
        prRepository = PullRequestRepository(self.session)
        userService = UsersService(self.session)
        
        managerIds = None
        if managerId is not None:
            managerIds = userService.get_manager_chain(managerId)
            
        if managerId is not None:
            reports = userService.get_all_reports(managerId, directOnly=False)
            total_swes = len(reports)
            total_swes_prev = len(reports)
        else:
            users_count = userService.get_all_users_count()
            total_swes = users_count
            total_swes_prev = users_count

        difference = end_date - start_date 
        start_date_prev = start_date - difference 
        end_date_prev = start_date
        
        result = prRepository.list_all(start_date, end_date, managers_ids=managerIds)
        result_prev = prRepository.list_all(start_date_prev, end_date_prev, managers_ids=managerIds)

        result = result.data if result else []
        result_prev = result_prev.data if result_prev else []

        unique_swes = len(set([pr["authorId"] for pr in result]))
        unique_swes_prev = len(set([pr["authorId"] for pr in result_prev]))

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

    def build_line_charts(self, managerId:int, start_date:datetime, end_date:datetime):
        date_range = [(start_date + datetime.timedelta(days=i)).date() for i in range((end_date - start_date).days + 1)]

        prRepository = PullRequestRepository(self.session)
        userService = UsersService(self.session)
        
        if managerId is not None:
            managerIds = userService.get_manager_chain(managerId)
            reports = userService.get_all_reports(managerId, directOnly=False)
            total_swes = len(reports)      
        else:
            users_count = userService.get_all_users_count()
            total_swes = users_count
            managerIds = None  

        result = prRepository.list_all(start_date, end_date, managerIds)
        result = result.data if result else []
        unique_swes = len(set([pr["authorId"] for pr in result]))
                    
        grouped_by_date = {}
        less100_grouped_by_date = {}
        active_swe_by_date = {}
        for pr in result:
            closed_date = pr["closedAt"].date()
            if closed_date not in grouped_by_date:
                grouped_by_date[closed_date] = 0
                less100_grouped_by_date[closed_date] = 0
                active_swe_by_date[closed_date] = set()
            grouped_by_date[closed_date] += 1   
            less100_grouped_by_date[closed_date] += 1 if pr["deletions"]+pr["additions"] <= 100 else 0
            active_swe_by_date[closed_date].add(pr["authorId"]) 

        # Calculate average total_duration_h per day
        average_duration_per_day = {}
        for pr in result:
            closed_date = pr["closedAt"].date()
            if closed_date not in average_duration_per_day:
                average_duration_per_day[closed_date] = []
            
            average_duration_per_day[closed_date].append(pr["totalDuration"])

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
    
    def build_user_stats(self, managerIds, start_date, end_date):
        prRepository = PullRequestRepository(self.session)
        userService = UsersService(self.session)
        reports = userService.get_all_reports(managerIds[0], directOnly=False)
        
        users_by_id = {user.id: user for user in reports}

        result = prRepository.get_pr_stats_group_by_user(start_date, end_date, managerIds)

        # Join result with users using users_by_id and add user field to every item in result
        for item in result:
            item["avg_duration"] = round(item["avg_duration"].total_seconds() / 3600, 2) 
            item["max_duration"] = round(item["max_duration"].total_seconds() / 3600, 2) 
            item["avg_loc"] = round(item["avg_loc"], 2) 
            user_id = item["authorId"]
            if user_id in users_by_id:
                user = users_by_id[user_id]
                item["user_name"] = user.name
                item["user_team"] = user.team.name
                item["user_gitAlias"] = user.gitAlias
            else:
                item["user"] = None

        return result