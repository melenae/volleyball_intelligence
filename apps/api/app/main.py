import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routes.analytics import router as analytics_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.matches import router as matches_router
from app.api.routes.players import router as players_router
from app.api.routes.seasons import router as seasons_router
from app.api.routes.teams import router as teams_router
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Volleyball Intelligence API",
        version="0.2.0",
        summary="Read-only analytics API over canonical PostgreSQL data.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["Accept", "Content-Type"],
    )
    register_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(seasons_router)
    application.include_router(teams_router)
    application.include_router(players_router)
    application.include_router(matches_router)
    application.include_router(analytics_router)
    application.include_router(dashboard_router)
    return application


app = create_app()
