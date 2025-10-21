from sqlalchemy import Column, Integer, String, UUID, ForeignKey, Table, select
from apps.activity.models import Activity
from utils.db import Base
from sqlalchemy.orm import relationship
from sqlalchemy import event
from sqlalchemy.exc import InvalidRequestError


class Organization(Base):
    """Модель организации"""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)

    building = relationship("Building", back_populates="organizations")
    phone = Column(String(12), nullable=True)
    activities = relationship(
        "Activity", secondary="organization_activities", back_populates="organizations"
    )

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"


organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column(
        "organization_id", Integer, ForeignKey("organizations.id"), primary_key=True
    ),
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
)


def restrict_activity_depth(mapper, connection, target):
    """Ограничивает уровень вложенности активности при вставке"""
    max_depth = 3
    if target.parent_id is not None:
        depth = _get_activity_depth(connection, target.parent_id)
        if depth >= max_depth:
            raise InvalidRequestError(
                f"Нельзя добавить еще один уровень вложенности. Максимальный уровень: {max_depth}"
            )


def _get_activity_depth(connection, activity_id: int) -> int:
    """Рекурсивно вычисляет глубину активности"""
    if not activity_id:
        return 0
    result = connection.execute(
        select(Activity.parent_id).where(Activity.id == activity_id)
    ).scalar()
    return 1 + _get_activity_depth(connection, result) if result else 1


event.listens_for(Activity, "before_insert")(restrict_activity_depth)
