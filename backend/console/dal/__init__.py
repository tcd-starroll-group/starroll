"""Data Access Layer module."""

from typing import Optional
from backend.console.dal.cache import RedisClient
from backend.config.settings import Settings


_redis_client: Optional[RedisClient] = None


def get_redis_client(settings: Optional[Settings] = None) -> RedisClient:
    """Get or create Redis client instance.

    Args:
        settings: Settings object (optional, will create instance if not provided)

    Returns:
        RedisClient instance
    """
    global _redis_client
    if _redis_client is None:
        if settings is None:
            settings = Settings()
        _redis_client = RedisClient.get_instance(settings)
    return _redis_client


__all__ = ["get_redis_client", "RedisClient"]
