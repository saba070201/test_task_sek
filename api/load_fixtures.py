import json
import asyncio

from utils.db import async_session, init_db
from apps.organization.models import Organization, organization_activities
from apps.building.models import Building
from apps.activity.models import Activity


async def populate_db():
    async with async_session() as session:
        async with session.begin():
            with open("./api/fixtures/buildings.json", "r", encoding="utf-8") as f:
                buildings_data = json.load(f)
            for building_data in buildings_data:
                building = Building(**building_data)
                session.add(building)
            await session.flush()

            with open("./api/fixtures/organizations.json", "r", encoding="utf-8") as f:
                organizations_data = json.load(f)
            for org_data in organizations_data:
                org = Organization(**org_data)
                session.add(org)
            await session.flush()

            with open("./api/fixtures/activities.json", "r", encoding="utf-8") as f:
                activities_data = json.load(f)
            for activity_data in activities_data:
                activity = Activity(**activity_data)
                session.add(activity)
            await session.flush()

            with open(
                "./api/fixtures/organization_activities.json", "r", encoding="utf-8"
            ) as f:
                org_activities_data = json.load(f)
            for link in org_activities_data:
                await session.execute(
                    organization_activities.insert().values(
                        organization_id=link["organization_id"],
                        activity_id=link["activity_id"],
                    )
                )

        await session.commit()
        print("Database populated successfully!")


async def main():
    await init_db()
    await populate_db()


if __name__ == "__main__":
    asyncio.run(main())
