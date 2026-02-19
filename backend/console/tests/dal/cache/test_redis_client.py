from unittest.mock import MagicMock, patch

import pytest
import redis

from backend.config.settings import Settings
from backend.console.dal.cache.client import RedisClient


@pytest.fixture(autouse=True)
def reset_singleton():
    RedisClient._instance = None
    yield
    RedisClient._instance = None


@pytest.fixture
def settings() -> Settings:
    return Settings()


def test_init_success(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis") as redis_cls:
        mock_conn = MagicMock()
        redis_cls.return_value = mock_conn

        client = RedisClient(settings)

        assert client.client is mock_conn
        mock_conn.ping.assert_called_once()
        redis_cls.assert_called_once_with(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30,
        )


def test_init_connection_error(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis") as redis_cls:
        mock_conn = MagicMock()
        mock_conn.ping.side_effect = redis.ConnectionError("boom")
        redis_cls.return_value = mock_conn

        with pytest.raises(ConnectionError, match="Failed to connect to Redis"):
            RedisClient(settings)


def test_get_instance_returns_singleton(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis"):
        first = RedisClient.get_instance(settings)
        second = RedisClient.get_instance(settings)

        assert first is second


def test_set_success(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis"):
        client = RedisClient(settings)

    assert client.set("k", "v", ex=10) is True
    client.client.set.assert_called_once_with("k", "v", ex=10)


def test_get_success(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis"):
        client = RedisClient(settings)
    client.client.get.return_value = "value"

    result = client.get("k")

    assert result == "value"
    client.client.get.assert_called_once_with("k")


def test_delete_many_with_empty_keys_returns_zero(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis"):
        client = RedisClient(settings)

    result = client.delete_many([])

    assert result == 0
    client.client.delete.assert_not_called()


def test_delete_many_success(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis"):
        client = RedisClient(settings)
    client.client.delete.return_value = 2

    result = client.delete_many(["a", "b"])

    assert result == 2
    client.client.delete.assert_called_once_with("a", "b")


def test_exists_true_when_redis_returns_positive(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis"):
        client = RedisClient(settings)
    client.client.exists.return_value = 1

    assert client.exists("k") is True
    client.client.exists.assert_called_once_with("k")


def test_incr_with_custom_amount(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis"):
        client = RedisClient(settings)
    client.client.incrby.return_value = 5

    result = client.incr("counter", amount=3)

    assert result == 5
    client.client.incrby.assert_called_once_with("counter", 3)


def test_set_raises_wrapped_exception_on_redis_error(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis"):
        client = RedisClient(settings)
    client.client.set.side_effect = redis.RedisError("set failed")

    with pytest.raises(Exception, match="Redis set operation failed"):
        client.set("k", "v")


def test_close_closes_connection_and_resets_singleton(settings: Settings):
    with patch("backend.console.dal.cache.client.redis.Redis"):
        instance = RedisClient.get_instance(settings)

    instance.close()

    instance.client.close.assert_called_once()
    assert RedisClient._instance is None
