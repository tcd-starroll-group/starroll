"""Data Access Layer module."""

from typing import Optional
from backend.console.dal.cache import RedisClient
from backend.console.dal.mq.client import KafkaClient
from backend.config.settings import Settings


_redis_client: Optional[RedisClient] = None
_kafka_client: Optional[KafkaClient] = None


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


def get_kafka_client(settings: Optional[Settings] = None) -> KafkaClient:
    """Get or create Kafka client instance.

    Args:
        settings: Settings object (optional, will create instance if not provided)

    Returns:
        KafkaClient instance
    """
    global _kafka_client
    if _kafka_client is None:
        if settings is None:
            settings = Settings()
        _kafka_client = KafkaClient.get_instance(settings)
    return _kafka_client


__all__ = ["get_redis_client", "get_kafka_client",
           "RedisClient", "KafkaClient"]
