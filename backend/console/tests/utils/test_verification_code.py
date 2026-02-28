import pytest
from unittest.mock import MagicMock, patch

from backend.console.utils.verification_code import VerificationCodeStore


class TestVerificationCodeStore:

    def setup_method(self):
        """Create a fresh store instance with a mocked Redis client before each test."""
        # Patch RedisClient.get_instance so no real Redis connection is made
        patcher = patch("backend.console.dal.cache.verification_code.RedisClient.get_instance")
        self.mock_get_instance = patcher.start()
        self.mock_redis = MagicMock()
        self.mock_get_instance.return_value = self.mock_redis
        self.store = VerificationCodeStore()
        self.addCleanup = patcher.stop

    def teardown_method(self):
        """Stop the patcher after each test."""
        self.addCleanup()

    def test_generate_code_returns_6_digits(self):
        """generate_verification_code() should return a 6-digit numeric string."""
        code = self.store.generate_verification_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_save_code_writes_to_redis(self):
        """save_verification_code() should call Redis set with the correct key and TTL."""
        self.store.save_verification_code("test@example.com", "123456")
        self.mock_redis.set.assert_called_once_with(
            "verification_code:test@example.com", "123456", ex=600
        )

    def test_verify_code_success(self):
        """verify_verification_code() should return True when the code matches."""
        self.mock_redis.get.return_value = "123456"
        result = self.store.verify_verification_code("test@example.com", "123456")
        assert result is True

    def test_verify_code_deletes_after_success(self):
        """After successful verification, the key should be deleted (one-time use)."""
        self.mock_redis.get.return_value = "123456"
        self.store.verify_verification_code("test@example.com", "123456")
        self.mock_redis.delete.assert_called_once_with("verification_code:test@example.com")

    def test_verify_code_wrong_code(self):
        """verify_verification_code() should return False when the code does not match."""
        self.mock_redis.get.return_value = "123456"
        result = self.store.verify_verification_code("test@example.com", "000000")
        assert result is False

    def test_verify_code_wrong_code_does_not_delete(self):
        """On a wrong code, the key should NOT be deleted."""
        self.mock_redis.get.return_value = "123456"
        self.store.verify_verification_code("test@example.com", "000000")
        self.mock_redis.delete.assert_not_called()

    def test_verify_code_email_not_found(self):
        """verify_verification_code() should return False when the key does not exist in Redis."""
        self.mock_redis.get.return_value = None
        result = self.store.verify_verification_code("unknown@example.com", "123456")
        assert result is False

    def test_verify_code_expired(self):
        """Expired keys return None from Redis, so verification should return False."""
        # Redis auto-expires keys; after expiry get() returns None
        self.mock_redis.get.return_value = None
        result = self.store.verify_verification_code("test@example.com", "123456")
        assert result is False

    def test_verify_code_one_time_use(self):
        """A verification code can only be used once."""
        # First call: code exists
        self.mock_redis.get.return_value = "123456"
        assert self.store.verify_verification_code("test@example.com", "123456") is True

        # Second call: key was deleted, Redis returns None
        self.mock_redis.get.return_value = None
        assert self.store.verify_verification_code("test@example.com", "123456") is False

    def test_generate_code_overwrites_previous(self):
        """Saving a new code for the same email overwrites the previous one."""
        self.store.save_verification_code("test@example.com", "111111")
        self.store.save_verification_code("test@example.com", "222222")

        # Redis set should have been called twice for the same key
        assert self.mock_redis.set.call_count == 2
        calls = [call.args[1] for call in self.mock_redis.set.call_args_list]
        assert calls == ["111111", "222222"]