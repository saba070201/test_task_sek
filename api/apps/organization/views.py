from fastapi import APIRouter, Depends, Request
from utils.db import get_session
from utils.auth import authenticate
from .schemas import (
    GetOrganizationListResponseSchema,
    GetOrganizationRequestSchema,
    OrganizationResponseSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from apps.organization.models import Organization
from apps.organization.services.busines import OrganizationBusinessService

router = APIRouter()


@router.get("", response_model=GetOrganizationListResponseSchema)
async def get_organization_list(
    request: Request,
    request_params: GetOrganizationRequestSchema = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    В зависимости от переданных параметров возвращает список организаций, при их отсутствии возвразает все организации.
    """
    return await OrganizationBusinessService.get_organizations(request_params, db=db)


@router.get("/{organization_id}", response_model=OrganizationResponseSchema)
async def get_organization_by_id(
    organization_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    Позволяет получить организацию по ее id
    """
    return await OrganizationBusinessService.get_organization_by_id(
        organization_id, db=db
    )
