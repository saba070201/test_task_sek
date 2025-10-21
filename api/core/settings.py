import os

from functools import lru_cache
from pydantic_settings import BaseSettings
from config.load_config import config


class Settings(BaseSettings):
    STATIC_API_KEY: str = config.get("app", {}).get("static_api_key")
    PORT: int = config.get("app", {}).get("port")
    HOST: str = config.get("app", {}).get("host")
    POSTGRES_USER: str = config.get("database", {}).get("user")
    POSTGRES_HOST: str = config.get("database", {}).get("host")
    POSTGRES_PORT: int = config.get("database", {}).get("port")
    POSTGRES__DB_NAME: str = config.get("database", {}).get("db_name")
    POSTGRES_PASS: str = config.get("database", {}).get("password")
    POSTGRES_URL: str = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES__DB_NAME}"
    )
    POSTGRES_CONN_TIMEOUT: int = 60
    POSTGRES_MIN_CONN_SIZE: int = 1
    POSTGRES_MAX_CONN_SIZE: int = 10
    LOG_LEVEL: str = config.get("app", {}).get("log_level", "INFO")


@lru_cache
def get_settings():
    return Settings()
