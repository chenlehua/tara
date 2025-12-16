"""
Application Settings
====================

Central configuration management using Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===== 通用配置 =====
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_secret_key: str = Field(
        default="change-me-in-production", alias="APP_SECRET_KEY"
    )
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")

    # ===== 服务端口 =====
    project_service_port: int = Field(default=8001, alias="PROJECT_SERVICE_PORT")
    document_service_port: int = Field(default=8002, alias="DOCUMENT_SERVICE_PORT")
    asset_service_port: int = Field(default=8003, alias="ASSET_SERVICE_PORT")
    threat_risk_service_port: int = Field(
        default=8004, alias="THREAT_RISK_SERVICE_PORT"
    )
    diagram_service_port: int = Field(default=8005, alias="DIAGRAM_SERVICE_PORT")
    report_service_port: int = Field(default=8006, alias="REPORT_SERVICE_PORT")
    agent_service_port: int = Field(default=8007, alias="AGENT_SERVICE_PORT")

    # ===== MySQL 配置 =====
    mysql_host: str = Field(default="localhost", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(default="tara", alias="MYSQL_USER")
    mysql_password: str = Field(default="tara_password", alias="MYSQL_PASSWORD")
    mysql_database: str = Field(default="tara_db", alias="MYSQL_DATABASE")

    @property
    def mysql_dsn(self) -> str:
        """Get MySQL connection string."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def mysql_async_dsn(self) -> str:
        """Get async MySQL connection string."""
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    # ===== Redis 配置 =====
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="", alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # ===== Neo4j 配置 =====
    neo4j_host: str = Field(default="localhost", alias="NEO4J_HOST")
    neo4j_bolt_port: int = Field(default=7687, alias="NEO4J_BOLT_PORT")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="neo4j_password", alias="NEO4J_PASSWORD")

    @property
    def neo4j_uri(self) -> str:
        """Get Neo4j connection URI."""
        return f"bolt://{self.neo4j_host}:{self.neo4j_bolt_port}"

    # ===== Milvus 配置 =====
    milvus_host: str = Field(default="localhost", alias="MILVUS_HOST")
    milvus_port: int = Field(default=19530, alias="MILVUS_PORT")
    milvus_user: str = Field(default="", alias="MILVUS_USER")
    milvus_password: str = Field(default="", alias="MILVUS_PASSWORD")

    # ===== ElasticSearch 配置 =====
    es_host: str = Field(default="localhost", alias="ES_HOST")
    es_port: int = Field(default=9200, alias="ES_PORT")
    es_user: str = Field(default="elastic", alias="ES_USER")
    es_password: str = Field(default="elastic_password", alias="ES_PASSWORD")

    @property
    def es_url(self) -> str:
        """Get ElasticSearch URL."""
        return f"http://{self.es_host}:{self.es_port}"

    # ===== MinIO 配置 =====
    minio_host: str = Field(default="localhost", alias="MINIO_HOST")
    minio_port: int = Field(default=9000, alias="MINIO_PORT")
    minio_access_key: str = Field(default="minio_access_key", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minio_secret_key", alias="MINIO_SECRET_KEY")
    minio_bucket_documents: str = Field(
        default="documents", alias="MINIO_BUCKET_DOCUMENTS"
    )
    minio_bucket_reports: str = Field(default="reports", alias="MINIO_BUCKET_REPORTS")
    minio_bucket_diagrams: str = Field(
        default="diagrams", alias="MINIO_BUCKET_DIAGRAMS"
    )

    @property
    def minio_endpoint(self) -> str:
        """Get MinIO endpoint."""
        return f"{self.minio_host}:{self.minio_port}"

    # ===== vLLM 模型服务配置 =====
    vllm_qwen3_vl_host: str = Field(default="localhost", alias="VLLM_QWEN3_VL_HOST")
    vllm_qwen3_vl_port: int = Field(default=8100, alias="VLLM_QWEN3_VL_PORT")
    vllm_qwen3_host: str = Field(default="localhost", alias="VLLM_QWEN3_HOST")
    vllm_qwen3_port: int = Field(default=8101, alias="VLLM_QWEN3_PORT")
    vllm_ocrflux_host: str = Field(default="localhost", alias="VLLM_OCRFLUX_HOST")
    vllm_ocrflux_port: int = Field(default=8102, alias="VLLM_OCRFLUX_PORT")
    vllm_embedding_host: str = Field(default="localhost", alias="VLLM_EMBEDDING_HOST")
    vllm_embedding_port: int = Field(default=8103, alias="VLLM_EMBEDDING_PORT")

    @property
    def qwen3_vl_url(self) -> str:
        """Get Qwen3-VL API URL."""
        return f"http://{self.vllm_qwen3_vl_host}:{self.vllm_qwen3_vl_port}/v1"

    @property
    def qwen3_url(self) -> str:
        """Get Qwen3 API URL."""
        return f"http://{self.vllm_qwen3_host}:{self.vllm_qwen3_port}/v1"

    @property
    def ocrflux_url(self) -> str:
        """Get OCRFlux API URL."""
        return f"http://{self.vllm_ocrflux_host}:{self.vllm_ocrflux_port}/v1"

    @property
    def embedding_url(self) -> str:
        """Get Embedding API URL."""
        return f"http://{self.vllm_embedding_host}:{self.vllm_embedding_port}/v1"

    # ===== Celery 配置 =====
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1", alias="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND"
    )

    # ===== JWT 配置 =====
    jwt_secret_key: str = Field(default="jwt-secret-key", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # ===== CORS 配置 =====
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"], alias="CORS_ORIGINS"
    )

    # ===== 文件上传配置 =====
    max_upload_size_mb: int = Field(default=100, alias="MAX_UPLOAD_SIZE_MB")
    allowed_extensions: str = Field(
        default="pdf,doc,docx,xls,xlsx,ppt,pptx,txt,dbc,json",
        alias="ALLOWED_EXTENSIONS",
    )

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get list of allowed file extensions."""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
