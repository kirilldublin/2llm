from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.session import init_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (sufficient for this learning project).
    await init_models()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    app.include_router(api_router)

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.APP_NAME}

    return app


app = create_app()
