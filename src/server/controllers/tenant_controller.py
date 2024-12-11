from fastapi import APIRouter
from app_context import context_user

router = APIRouter()


@router.get("/tenant")
def get_tenant():
    user = context_user.get()
    return user.tenant.to_dict()
