from fastapi import APIRouter, Response

from app.core.config import get_settings
from app.db.session import database_status
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse}},
)
def health(response: Response) -> HealthResponse:
    settings = get_settings()
    database = database_status()
    if database != "ok":
        response.status_code = 503
        return HealthResponse(
            status="degraded",
            service="volleyball-intelligence-api",
            environment=settings.app_env,
            database=database,
        )
    return HealthResponse(
        status="ok",
        service="volleyball-intelligence-api",
        environment=settings.app_env,
        database=database,
    )
