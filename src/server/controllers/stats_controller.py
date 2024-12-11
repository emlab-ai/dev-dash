from fastapi import APIRouter, Request
from controllers.utils import _get_request_scope_args
from services.statsService import StatsService
from app_context import context_session, context_user

router = APIRouter()


@router.get("/stats")
def get_stats(request: Request):
    managerId, start_date, end_date = _get_request_scope_args(request)

    statsService = StatsService(context_session.get())
    tenant = context_user.get().tenant
    cues = statsService.build_cues(tenant.id, managerId, start_date, end_date)
    line_charts = statsService.build_line_charts(
        tenant.id, managerId, start_date, end_date
    )

    return {"lineCharts": line_charts, "cues": cues}
