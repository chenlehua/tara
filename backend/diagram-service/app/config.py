"""Diagram service configuration."""
from tara_shared.config import Settings as BaseSettings


class ServiceSettings(BaseSettings):
    """Service specific settings."""
    
    SERVICE_NAME: str = "diagram-service"
    VERSION: str = "0.1.0"
    PORT: int = 8005
    API_PREFIX: str = "/api/v1"


settings = ServiceSettings()
