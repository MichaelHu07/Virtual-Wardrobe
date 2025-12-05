from app.schemas.health import HealthCheck
from app.core.config import settings

class HealthService:
    @staticmethod
    async def get_health() -> HealthCheck:
        return HealthCheck(
            name=settings.PROJECT_NAME,
            status="ok",
            version="1.0.0" # Ideally, this comes from a version file or config
        )

