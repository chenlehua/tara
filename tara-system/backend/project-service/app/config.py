"""
Service Configuration
=====================

Configuration for Project Management Service.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfig(BaseSettings):
    """Service-specific configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service info
    service_name: str = "tara-project-service"
    service_version: str = "0.1.0"
    service_port: int = 8001
    
    # API settings
    api_prefix: str = "/api/v1"
    
    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100


@lru_cache()
def get_config() -> ServiceConfig:
    """Get cached service configuration."""
    return ServiceConfig()


config = get_config()
