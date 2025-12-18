"""Report service configuration."""

from app.common.config import Settings as BaseSettings


class ServiceSettings(BaseSettings):
    """Service specific settings."""

    SERVICE_NAME: str = "report-service"
    VERSION: str = "0.1.0"
    PORT: int = 8006
    API_PREFIX: str = "/api/v1"


settings = ServiceSettings()
