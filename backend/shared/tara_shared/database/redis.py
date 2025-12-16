"""
Redis Connection
================

Redis client for caching and pub/sub.
"""

from typing import Optional

import redis
from redis import Redis

from ..config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Redis client wrapper with connection management."""

    _instance: Optional[Redis] = None
    _connection_error: Optional[str] = None

    @classmethod
    def get_client(cls) -> Optional[Redis]:
        """Get Redis client instance (singleton)."""
        if cls._instance is None and cls._connection_error is None:
            try:
                cls._instance = redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                )
                # Test connection
                cls._instance.ping()
                logger.info(f"Connected to Redis at {settings.redis_host}:{settings.redis_port}")
            except Exception as e:
                cls._connection_error = str(e)
                logger.warning(f"Failed to connect to Redis: {e}. Caching will be unavailable.")
                cls._instance = None
        return cls._instance

    @classmethod
    def is_available(cls) -> bool:
        """Check if Redis is available."""
        return cls.get_client() is not None

    @classmethod
    def close(cls) -> None:
        """Close Redis connection."""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
            cls._connection_error = None


def get_redis() -> Optional[Redis]:
    """Get Redis client for dependency injection."""
    return RedisClient.get_client()


# Lazy-initialized global client
redis_client: Optional[Redis] = None


def get_redis_client() -> Optional[Redis]:
    """Get global Redis client with lazy initialization."""
    global redis_client
    if redis_client is None:
        redis_client = RedisClient.get_client()
    return redis_client


def get_redis() -> Redis:
    """Get Redis client for dependency injection."""
    return RedisClient.get_client()


class CacheService:
    """Cache service for common caching operations."""

    def __init__(self, client: Redis = None, prefix: str = "tara"):
        self._client = client
        self._lazy_client = client is None
        self.prefix = prefix

    @property
    def client(self) -> Optional[Redis]:
        """Get client with lazy initialization."""
        if self._lazy_client and self._client is None:
            self._client = get_redis_client()
        return self._client

    def is_available(self) -> bool:
        """Check if cache service is available."""
        return self.client is not None

    def _key(self, key: str) -> str:
        """Build cache key with prefix."""
        return f"{self.prefix}:{key}"

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.is_available():
            return None
        try:
            return self.client.get(self._key(key))
        except Exception:
            return None

    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Set value in cache with expiration."""
        if not self.is_available():
            return False
        try:
            return self.client.setex(self._key(key), expire, value)
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.is_available():
            return False
        try:
            return bool(self.client.delete(self._key(key)))
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.is_available():
            return False
        try:
            return bool(self.client.exists(self._key(key)))
        except Exception:
            return False

    def set_json(self, key: str, data: dict, expire: int = 3600) -> bool:
        """Set JSON data in cache."""
        import json
        return self.set(key, json.dumps(data), expire)

    def get_json(self, key: str) -> Optional[dict]:
        """Get JSON data from cache."""
        import json
        data = self.get(key)
        if data:
            return json.loads(data)
        return None

    def incr(self, key: str) -> int:
        """Increment counter."""
        if not self.is_available():
            return 0
        try:
            return self.client.incr(self._key(key))
        except Exception:
            return 0

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        if not self.is_available():
            return False
        try:
            return self.client.expire(self._key(key), seconds)
        except Exception:
            return False


# Lazy-initialized global cache service
cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get global cache service with lazy initialization."""
    global cache_service
    if cache_service is None:
        cache_service = CacheService()
    return cache_service
