from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from core.settings import get_settings
from apps.organization.router import organizations_router

settings = get_settings()


class SuperHttpBearer(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPException | None:

        if (
            not request.headers.get("Authorization")
            == f"Bearer {settings.STATIC_API_KEY}"
        ):
            raise HTTPException(status_code=401, detail="Unauthorized.")


security = SuperHttpBearer()
router = APIRouter()
router.include_router(organizations_router, dependencies=[Depends(security)])
