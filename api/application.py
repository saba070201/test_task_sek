import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from fastapi import FastAPI

from alembic import command
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from apps.router import router
from core.settings import get_settings
from alembic.config import Config
from utils.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    settings = get_settings()

    def apply_migrations():
        logger.info("Starting Alembic migrations...")
        try:
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            logger.info("Alembic migrations applied successfully")
        except Exception as e:
            logger.error(f"Failed to apply migrations: {str(e)}")
            raise

    async def run_migrations_in_thread():
        logger.info("Running migrations in thread...")
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, apply_migrations)

    app = FastAPI(
        redoc_url="/redoc/",
        docs_url="/docs/",
        openapi_url="/api/openapi.json",
    )

    app.include_router(prefix="/v1", router=router)

    @app.on_event("startup")
    async def startup_event():
        logger.info("Initializing database...")
        await init_db()
        logger.info("Applying migrations...")
        await run_migrations_in_thread()

    return app
