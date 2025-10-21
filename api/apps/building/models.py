from sqlalchemy import Column, Integer, String, ARRAY, Float
from utils.db import Base
from sqlalchemy.orm import relationship
from utils.logger import get_logger

logger = get_logger(__name__)


class Building(Base):
    """Модель здания"""

    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(500), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    organizations = relationship(
        "Organization", back_populates="building", uselist=False
    )

    def __repr__(self):
        return f"<Building(id={self.id}, address='{self.address[:50]}...')>"
