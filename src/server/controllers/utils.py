from datetime import datetime
from fastapi import Request


def _get_request_date_args(request: Request) -> tuple[datetime, datetime]:
    start_date_str = request.query_params.get("start_date")
    end_date_str = request.query_params.get("end_date")
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    return start_date, end_date


def _get_request_scope_args(request: Request) -> tuple[int, datetime, datetime]:
    start_date, end_date = _get_request_date_args(request)
    managerId = request.query_params.get("manager_id")

    return managerId, start_date, end_date
