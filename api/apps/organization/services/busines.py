from typing import List, Set
from apps.organization.models import Organization, organization_activities
from apps.activity.models import Activity
from apps.building.models import Building
from apps.organization.schemas import (
    BuildingSchema,
    GetOrganizationListResponseSchema,
    GetOrganizationsByGeoRequestSchema,
    GetOrganizationsRequestSchema,
    OrganizationResponseSchema,
    ActivityTreeSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func, select, or_
from geopy.distance import geodesic
from utils.logger import get_logger

logger = get_logger(__name__)


class OrganizationBusinessService:
    @classmethod
    async def __serialize_list_response(
        cls, organizations, db: AsyncSession
    ) -> GetOrganizationListResponseSchema:
        """
        Функция для сериализации списка организаций для ЛЮБОГО запроса с поиском организаций
        """
        logger.debug(
            "Serializing %d organizations", len(organizations) if organizations else 0
        )
        __organizations = []
        for org in organizations:
            org.activity_tree = await cls.__build_activity_tree_for_org(
                org.activities, db
            )
            org.phone_number = org.phone
            __organizations.append(
                OrganizationResponseSchema(
                    id=org.id,
                    name=org.name,
                    building=BuildingSchema(
                        id=org.building.id,
                        address=org.building.address,
                        latitude=org.building.latitude,
                        longitude=org.building.longitude,
                    ),
                    activity_tree=org.activity_tree,
                    phone_number=org.phone,
                )
            )
        return GetOrganizationListResponseSchema(organizations=__organizations)

    @classmethod
    async def __build_activity_tree_for_org(
        cls,
        activities,
        db: AsyncSession,
    ) -> List[ActivityTreeSchema]:
        """Строит дерево активностей для одной организации"""

        async def _collect_parents(db: AsyncSession, activity: Activity, ids: Set[int]):
            """Рекурсивно собирает ID родителей активности"""
            ids.add(activity.id)
            if activity.parent_id and activity.parent is None:
                # Если parent не подгружен, загружаем явно
                stmt = (
                    select(Activity)
                    .where(Activity.id == activity.parent_id)
                    .options(selectinload(Activity.parent))
                )
                result = await db.execute(stmt)
                activity.parent = result.scalars().first()
            if activity.parent:
                await _collect_parents(db, activity.parent, ids)
                if not activities:
                    return []

        activity_ids = set()
        for act in activities:
            await _collect_parents(db, act, activity_ids)

        stmt = (
            select(Activity)
            .where(Activity.id.in_(activity_ids))
            .options(selectinload(Activity.children).selectinload(Activity.children))
        )
        result = await db.execute(stmt)
        all_activities = result.scalars().all()

        # Создаём словарь для быстрого доступа
        activity_map = {act.id: act for act in all_activities}

        root_ids = [act.id for act in all_activities if act.parent_id is None]
        if not root_ids:
            root_ids = list(activity_ids - {act.id for act in activities})

        roots = [act for act in all_activities if act.id in root_ids]

        def _build_tree(act: Activity) -> ActivityTreeSchema:
            children = [
                _build_tree(activity_map[child.id])
                for child in act.children
                if child.id in activity_ids
            ]
            return ActivityTreeSchema(id=act.id, name=act.name, children=children)

        return [_build_tree(root) for root in roots]

    @classmethod
    async def __get_organization_by_building(
        cls, building: str, db: AsyncSession
    ) -> GetOrganizationListResponseSchema:
        """
        Позволяет искать организации по зданию, можно ввести id постройки или ее название
        """
        logger.info("Searching organizations by building: %s", building)
        query = select(Organization).options(
            selectinload(Organization.building),
            selectinload(Organization.activities)
            .selectinload(Activity.parent)
            .selectinload(Activity.children),
        )
        query = query.join(
            Building, Organization.building_id == Building.id, isouter=False
        ).filter(Building.address.ilike(f"%{building}%"))
        result = await db.execute(query)
        organizations = result.scalars().unique().all()
        return await cls.__serialize_list_response(organizations, db)

    @classmethod
    async def __get_organizations_by_activity(
        cls, activity: str, db: AsyncSession
    ) -> GetOrganizationListResponseSchema:
        """
        Позволяет искать организации по видам деятельности, можно ввести id вида деятельности или его название
        """
        logger.info("Searching organizations by activity: %s", activity)
        query = select(Organization).options(
            selectinload(Organization.building),
            selectinload(Organization.activities)
            .selectinload(Activity.parent)
            .selectinload(Activity.children),
        )

        if activity.isdigit():
            activity_id = int(activity)
            query = query.filter(
                or_(Activity.id == activity_id, Activity.name.ilike(f"%{activity}%"))
            )
        else:
            query = (
                query.join(
                    organization_activities,
                    organization_activities.c.organization_id == Organization.id,
                    isouter=False,
                )
                .join(
                    Activity,
                    organization_activities.c.activity_id == Activity.id,
                    isouter=False,
                )
                .filter(Activity.name.ilike(f"%{activity}%"))
            )

        result = await db.execute(query)
        organizations = result.scalars().unique().all()
        return await cls.__serialize_list_response(organizations, db)

    @classmethod
    async def __get_organizations_by_name(
        cls, name: str, db: AsyncSession
    ) -> GetOrganizationListResponseSchema:
        """
        Позволяет искать организации по имени, можно ввести полное или частичное имя организации или его id
        """
        logger.info("Searching organizations by name: %s", name)
        query = select(Organization).options(
            selectinload(Organization.building),
            selectinload(Organization.activities)
            .selectinload(Activity.parent)
            .selectinload(Activity.children),
        )
        if name.isdigit():
            query = query.filter(
                or_(Organization.id == int(name)), Organization.name.ilike(f"%{name}%")
            )
        else:
            query = query.filter(Organization.name.ilike(f"%{name}%"))
        result = await db.execute(query)
        organizations = result.scalars().unique().all()
        return await cls.__serialize_list_response(organizations, db)

    @classmethod
    async def __get_all_organizations(
        cls, db: AsyncSession
    ) -> GetOrganizationListResponseSchema:
        """
        Позволяет получить все организации
        """
        logger.info("Fetching all organizations from DB")
        query = select(Organization).options(
            selectinload(Organization.building), selectinload(Organization.activities)
        )
        result = await db.execute(query)
        organizations = result.scalars().all()
        return await cls.__serialize_list_response(organizations, db)

    @classmethod
    async def __get_organizations_by_geo(
        cls, latitude: float, longitude: float, radius: int, db: AsyncSession
    ) -> GetOrganizationListResponseSchema:
        """
        Позволяет искать организации по геолокации (широта и долгота)
        """
        logger.info(
            "Searching organizations by geo coords: (%s, %s)", latitude, longitude
        )
        query = select(Organization).options(
            selectinload(Organization.building),
            selectinload(Organization.activities)
            .selectinload(Activity.parent)
            .selectinload(Activity.children),
        )

        def is_within_radius(org):
            # TODO : исправить бы на pg-геолокацию
            org_location = (org.building.latitude, org.building.longitude)
            user_location = (latitude, longitude)
            distance = geodesic(user_location, org_location).meters
            return distance <= radius

        result = await db.execute(query)
        organizations = list(filter(is_within_radius, result.scalars().all()))

        return await cls.__serialize_list_response(organizations, db)

    @classmethod
    async def get_organizations(
        cls,
        query_params: (
            GetOrganizationsRequestSchema | GetOrganizationsByGeoRequestSchema
        ),
        db: AsyncSession,
    ):
        """
        Точка входа в бизнес логику организаций.
        В зависимости от query_param вызывает один из приватных методов для поиска организаций
        по зданию, виду деятельности или имени
        """
        logger.debug("get_organizations called with params: %s", query_params)
        if isinstance(query_params, GetOrganizationsByGeoRequestSchema):
            return await cls.__get_organizations_by_geo(
                query_params.current_latitude,
                query_params.current_longitude,
                query_params.radius,
                db,
            )
        if query_params.building_name:
            return await cls.__get_organization_by_building(
                query_params.building_name, db
            )
        elif query_params.organization_name:
            return await cls.__get_organizations_by_name(
                query_params.organization_name, db
            )
        elif query_params.activity_name:
            return await cls.__get_organizations_by_activity(
                query_params.activity_name, db
            )
        else:
            return await cls.__get_all_organizations(db)

    @classmethod
    async def get_organization_by_id(
        cls, organization_id: int, db: AsyncSession
    ) -> OrganizationResponseSchema:
        """
        Позволяет получить организацию по ее id
        """
        logger.info("Fetching organization by id: %s", organization_id)
        result = await db.execute(
            select(Organization)
            .options(
                selectinload(Organization.building),
                selectinload(Organization.activities),
            )
            .where(Organization.id == organization_id)
        )
        organization = result.scalars().first()
        return OrganizationResponseSchema(
            id=organization.id,
            name=organization.name,
            building=BuildingSchema(
                id=organization.building.id,
                address=organization.building.address,
                latitude=organization.building.latitude,
                longitude=organization.building.longitude,
            ),
            activity_tree=await cls.__build_activity_tree_for_org(
                organization.activities, db
            ),
            phone_number=organization.phone,
        )
