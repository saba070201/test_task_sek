import uvicorn
from application import create_app
from core.settings import get_settings

app = create_app()
settings = get_settings()


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
