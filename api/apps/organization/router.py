from fastapi import APIRouter

from .views import router as org_router

organizations_router = APIRouter(
    prefix="/organizations",
    tags=["Organization Module"],
)

organizations_router.include_router(
    org_router,
    prefix="/organization",
)
