from fastapi import APIRouter
from apps.organization.router import organizations_router

router = APIRouter()
router.include_router(organizations_router)
