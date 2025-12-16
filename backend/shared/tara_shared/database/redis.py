"""
Redis Connection
================

Redis client for caching and pub/sub.
"""

from typing import Optional

import redis
from redis import Redis

from ..config import settings


class RedisClient:
    """Redis client wrapper with connection management."""

    _instance: Optional[Redis] = None

    @classmethod
    def get_client(cls) -> Redis:
        """Get Redis client instance (singleton)."""
        if cls._instance is None:
            cls._instance = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )
        return cls._instance

    @classmethod
    def close(cls) -> None:
        """Close Redis connection."""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None


# Global client instance
redis_client = RedisClient.get_client()


def get_redis() -> Redis:
    """Get Redis client for dependency injection."""
    return RedisClient.get_client()


class CacheService:
    """Cache service for common caching operations."""

    def __init__(self, client: Redis = None, prefix: str = "tara"):
        self.client = client or redis_client
        self.prefix = prefix

    def _key(self, key: str) -> str:
        """Build cache key with prefix."""
        return f"{self.prefix}:{key}"

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return self.client.get(self._key(key))

    def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Set value in cache with expiration."""
        return self.client.setex(self._key(key), expire, value)

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        return bool(self.client.delete(self._key(key)))

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return bool(self.client.exists(self._key(key)))

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
        return self.client.incr(self._key(key))

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        return self.client.expire(self._key(key), seconds)


# Global cache service
cache_service = CacheService()
