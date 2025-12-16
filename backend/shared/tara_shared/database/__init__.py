"""Database connection modules."""

# MySQL is always required
from .mysql import SessionLocal, engine, get_db, init_db

# Optional imports - these may not be available in all environments
try:
    from .elasticsearch import es_client, get_es_client, get_search_service
except ImportError:
    es_client = None
    get_es_client = lambda: None
    get_search_service = lambda: None

try:
    from .milvus import get_milvus_client, get_vector_service, init_milvus
except ImportError:
    get_milvus_client = lambda: None
    get_vector_service = lambda: None
    init_milvus = lambda: None

try:
    from .minio import get_minio_client, get_storage_service, minio_client
except ImportError:
    minio_client = None
    get_minio_client = lambda: None
    get_storage_service = lambda: None

try:
    from .neo4j import get_graph_service, get_neo4j_driver, neo4j_driver
except ImportError:
    neo4j_driver = None
    get_neo4j_driver = lambda: None
    get_graph_service = lambda: None

try:
    from .redis import get_cache_service, get_redis, redis_client
except ImportError:
    redis_client = None
    get_redis = lambda: None
    get_cache_service = lambda: None

__all__ = [
    # MySQL
    "get_db",
    "init_db",
    "engine",
    "SessionLocal",
    # Redis
    "get_redis",
    "redis_client",
    "get_cache_service",
    # Neo4j
    "get_neo4j_driver",
    "neo4j_driver",
    "get_graph_service",
    # Milvus
    "get_milvus_client",
    "init_milvus",
    "get_vector_service",
    # ElasticSearch
    "get_es_client",
    "es_client",
    "get_search_service",
    # MinIO
    "get_minio_client",
    "minio_client",
    "get_storage_service",
]
