from typing import List, Set
from apps.organization.models import Organization, organization_activities
from apps.activity.models import Activity
from apps.organization.schemas import (
    BuildingSchema,
    GetOrganizationListResponseSchema,
    GetOrganizationRequestSchema,
    OrganizationResponseSchema,
    ActivityTreeSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, or_


class OrganizationBusinessService:
    @classmethod
    async def __serialize_list_response(
        cls, organizations, db: AsyncSession
    ) -> GetOrganizationListResponseSchema:
        """
        Функция для сериализации списка организаций для ЛЮБОГО запроса с поиском организаций
        """
        __organizations = []
        for org in organizations:
            org.activity_tree = cls.__build_activity_tree_for_org(org.activities)
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
                    phone_number=org.phone_number,
                )
            )
        return GetOrganizationListResponseSchema(organizations=__organizations)

    @classmethod
    def __build_activity_tree_for_org(
        cls, activities: List[Activity]
    ) -> List[ActivityTreeSchema]:
        def _collect_parents(activity: Activity, ids: Set[int]):
            ids.add(activity.id)
            if activity.parent:
                _collect_parents(activity.parent, ids)

        def _build_tree(act: Activity) -> ActivityTreeSchema:
            children = [
                _build_tree(child) for child in act.children if child.id in activity_ids
            ]
            return ActivityTreeSchema(id=act.id, name=act.name, children=children)#type: ignore

        if not activities:
            return []

        activity_ids = set()
        for act in activities:
            _collect_parents(act, activity_ids)

        root_ids = [act.id for act in activities if act.parent_id is None]
        if not root_ids:
            root_ids = list(activity_ids - {act.id for act in activities})

        roots = [act for act in activities if act.id in root_ids]

        return [_build_tree(root) for root in roots]

    @classmethod
    async def __get_organization_by_building(cls, building: str, db: AsyncSession) -> GetOrganizationListResponseSchema:
        """
        Позволяет искать организации по зданию, можно ввести id постройки или ее название
        """
        stmt = select(Organization).options(
            selectinload(Organization.building), selectinload(Organization.activities)
        )
        if building.isdigit():
            stmt = stmt.where(
                or_(Organization.id == int(building)),
                Organization.name.ilike(f"%{building}%"),
            )
        else:
            stmt = stmt.where(Organization.name.ilike(f"%{building}%"))
        result = await db.execute(stmt)
        organizations = result.scalars().all()
        return await cls.__serialize_list_response(organizations, db)

    @classmethod
    async def __get_organizations_by_activity(cls, activity: str, db: AsyncSession) -> GetOrganizationListResponseSchema:
        """
        Позволяет искать организации по видам деятельности, можно ввести id вида деятельности или его название
        """
        stmt = select(Organization).options(
            selectinload(Organization.building), selectinload(Organization.activities)
        )

        if activity:
            stmt = stmt.join(organization_activities).join(Activity)
            if activity.isdigit():
                stmt = stmt.where(Activity.id == int(activity))
            else:
                stmt = stmt.where(Activity.name.ilike(f"%{activity}%"))

        result = await db.execute(stmt)
        organizations = result.scalars().all()
        return await cls.__serialize_list_response(organizations, db)

    @classmethod
    async def __get_organizations_by_name(cls, name: str, db: AsyncSession) -> GetOrganizationListResponseSchema:
        """
        Позволяет искать организации по имени, можно ввести полное или частичное имя организации или его id
        """
        stmt = select(Organization).options(
            selectinload(Organization.building), selectinload(Organization.activities)
        )
        if name.isdigit():
            stmt = stmt.where(
                or_(Organization.id == int(name)), Organization.name.ilike(f"%{name}%")
            )
        else:
            stmt = stmt.where(Organization.name.ilike(f"%{name}%"))
        result = await db.execute(stmt)
        organizations = result.scalars().all()
        return await cls.__serialize_list_response(organizations, db)

    @classmethod
    async def __get_all_organizations(
        cls, db: AsyncSession
    ) -> GetOrganizationListResponseSchema:
        """
        Позволяет получить все организации
        """
        stmt = select(Organization).options(
            selectinload(Organization.building), selectinload(Organization.activities)
        )
        result = await db.execute(stmt)
        organizations = result.scalars().all()
        stmt = select(Organization).options(
            selectinload(Organization.building), selectinload(Organization.activities)
        )
        result = await db.execute(stmt)
        organizations = result.scalars().all()
        return await cls.__serialize_list_response(organizations, db)

    @classmethod
    async def get_organizations(
        cls, query_param: GetOrganizationRequestSchema, db: AsyncSession
    ):
        """
        Точка входа в бизнес логику организаций.
        В зависимости от query_param вызывает один из приватных методов для поиска организаций
        по зданию, виду деятельности или имени
        """
        match query_param:
            case GetOrganizationRequestSchema(building_name=building_name) if (
                building_name is not None
            ):
                return await cls.__get_organization_by_building(building_name, db)
            case GetOrganizationRequestSchema(activity_name=activity_name) if (
                activity_name is not None
            ):
                return await cls.__get_organizations_by_activity(activity_name, db)
            case GetOrganizationRequestSchema(organization_name=organization_name) if (
                organization_name is not None
            ):
                return await cls.__get_organizations_by_name(organization_name, db)
            case _:
                return await cls.__get_all_organizations(db)

    @classmethod
    async def get_organization_by_id(cls, organization_id: int,db : AsyncSession) -> OrganizationResponseSchema:
        """
        Позволяет получить организацию по ее id
        """
        result = await db.execute(select(Organization).options(
            selectinload(Organization.building), selectinload(Organization.activities)
        ).where(Organization.id == organization_id))
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
            activity_tree=cls.__build_activity_tree_for_org(organization.activities),
            phone_number=organization.phone,
        )

