from fastapi import APIRouter, Request, Depends
from app.schemas.health import HealthCheck
from app.services.health import HealthService
from app.middlewares.rate_limiter import limiter

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
@limiter.limit("5/minute")
async def health_check(request: Request) -> HealthCheck:
    """
    Health check endpoint.
    """
    return await HealthService.get_health()

