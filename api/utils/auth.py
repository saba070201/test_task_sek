from core.settings import get_settings
from starlette.exceptions import HTTPException
import functools
from fastapi import Request


settings = get_settings()


def authenticate(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs["request"]
        if (
            not request.headers.get("Authorization")
            == f"Bearer {settings.STATIC_API_KEY}"
        ):
            raise HTTPException(status_code=401, detail="Unauthorized.")
        return await f(*args, **kwargs)

    return wrapper
