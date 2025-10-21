from apps.building.models import Building
from apps.organization.models import Organization


def create_building(session, name, address):
    building = Building(name=name, address=address)
    session.add(building)
    session.commit()
    return building


def create_organization(
    session, name, phone_number, building, kind_of_activity, activities
):
    organization = Organization(
        name=name,
        phone_number=phone_number,
        building=building,
        kind_of_activity=kind_of_activity,
    )
    for activity in activities:
        organization.activities.append(activity)
    session.add(organization)
    session.commit()
    return organization


def load_fixtures(session): ...
