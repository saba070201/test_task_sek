from sqlalchemy import Column, Float, Integer, String, ForeignKey
from utils.db import Base
from sqlalchemy.orm import relationship
from utils.logger import get_logger

logger = get_logger(__name__)


class Activity(Base):
    """Модель вида деятельности с древовидной структурой"""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship("Activity", back_populates="parent")

    organizations = relationship(
        "Organization", secondary="organization_activities", back_populates="activities"
    )

    def __repr__(self):
        return f"<Activity(id={self.id}, name='{self.name}')>"
