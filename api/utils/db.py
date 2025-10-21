from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from core.settings import get_settings
from .logger import get_logger

logger = get_logger(__name__)

settings = get_settings()
engine = create_async_engine(settings.POSTGRES_URL, echo=True)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    logger.info("Initializing database and creating tables if not exist")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def get_session() -> AsyncSession:
    logger.debug("Opening new DB session")
    async with async_session() as session:
        yield session
    logger.debug("DB session closed")
