from fastapi import APIRouter, Depends, Request
from utils.db import get_session
from utils.auth import authenticate
from .schemas import (
    GetOrganizationListResponseSchema,
    GetOrganizationsRequestSchema,
    OrganizationResponseSchema,
    GetOrganizationsByGeoRequestSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession
from apps.organization.services.busines import OrganizationBusinessService
from utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("", response_model=GetOrganizationListResponseSchema)
async def get_organization_list(
    request: Request,
    query_params: GetOrganizationsRequestSchema = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    В зависимости от переданных параметров возвращает список организаций, при их отсутствии возвразает все организации.
    """
    logger.debug("HTTP get_organization_list called with params: %s", query_params)
    return await OrganizationBusinessService.get_organizations(
        query_params=query_params, db=db
    )


@router.get("/search-by-geo", response_model=GetOrganizationListResponseSchema)
async def search_organizations_by_geo(
    request: Request,
    query_params: GetOrganizationsByGeoRequestSchema = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    Позволяет искать организации по геолокации (широта и долгота)
    """
    logger.debug(
        "HTTP search_organizations_by_geo called with coords: (%s, %s) and radius: %s",
        query_params.current_latitude,
        query_params.current_longitude,
        query_params.radius,
    )
    return await OrganizationBusinessService.get_organizations(
        db=db, query_params=query_params
    )


@router.get("/{organization_id}", response_model=OrganizationResponseSchema)
async def get_organization_by_id(
    organization_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    Позволяет получить организацию по ее id
    """
    logger.debug("HTTP get_organization_by_id called with id: %s", organization_id)
    return await OrganizationBusinessService.get_organization_by_id(
        organization_id, db=db
    )
