import datetime
import time

import jwt
import pytest

from backend.console.utils.auth import create_access_token, verify_access_token
from backend.config import settings


class TestCreateAccessToken:
    def test_create_access_token_success(self):
        """Test successful token creation with valid data."""
        data = {"sub": "alice", "user_id": 123}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert token  # Token should not be empty

    def test_create_access_token_contains_payload(self):
        """Test that the created token contains the provided data."""
        data = {"sub": "bob", "user_id": 456}
        token = create_access_token(data)

        # Decode without verification to check payload
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["sub"] == "bob"
        assert payload["user_id"] == 456
        assert "exp" in payload

    def test_create_access_token_has_expiration(self):
        """Test that the created token has proper expiration time."""
        data = {"sub": "carol"}
        before_creation = datetime.datetime.now(datetime.timezone.utc)
        token = create_access_token(data)
        after_creation = datetime.datetime.now(datetime.timezone.utc)

        payload = jwt.decode(token, options={"verify_signature": False})
        exp_time = datetime.datetime.fromtimestamp(
            payload["exp"], tz=datetime.timezone.utc
        )

        # Expiration should be approximately jwt_expire_hours from now
        expected_min = before_creation + datetime.timedelta(
            hours=settings.jwt_expire_hours - 1
        )
        expected_max = after_creation + datetime.timedelta(
            hours=settings.jwt_expire_hours + 1
        )
        assert expected_min <= exp_time <= expected_max


class TestVerifyAccessToken:
    def test_verify_access_token_success(self):
        """Test successful token verification."""
        data = {"sub": "dave", "user_id": 789}
        token = create_access_token(data)

        payload, is_valid = verify_access_token(token)
        assert is_valid is True
        assert payload is not None
        assert payload["sub"] == "dave"
        assert payload["user_id"] == 789

    def test_verify_access_token_invalid_token(self):
        """Test verification with invalid token format."""
        payload, is_valid = verify_access_token("invalid.token.here")
        assert is_valid is False
        assert payload is None

    def test_verify_access_token_corrupted_signature(self):
        """Test verification with corrupted token signature."""
        data = {"sub": "eve"}
        token = create_access_token(data)
        # Tamper with the token
        corrupted_token = token[:-10] + "aaaaaaaaaa"

        payload, is_valid = verify_access_token(corrupted_token)
        assert is_valid is False
        assert payload is None

    def test_verify_access_token_expired(self):
        """Test verification with expired token."""
        # Create a token with very short expiration
        data = {"sub": "frank"}
        to_encode = data.copy()
        expire = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(seconds=1)
        to_encode.update({"exp": expire})
        expired_token = jwt.encode(
            to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
        )

        payload, is_valid = verify_access_token(expired_token)
        assert is_valid is False
        assert payload is None

    def test_verify_access_token_wrong_secret(self, monkeypatch: pytest.MonkeyPatch):
        """Test verification fails when secret key is changed."""
        data = {"sub": "grace"}
        token = create_access_token(data)

        # Temporarily change the secret (32+ bytes to avoid warnings)
        original_secret = settings.jwt_secret
        try:
            monkeypatch.setattr(
                settings, "jwt_secret", "a_different_secret_key_that_is_long_enough_for_hmac_sha256"
            )
            payload, is_valid = verify_access_token(token)
            assert is_valid is False
            assert payload is None
        finally:
            settings.jwt_secret = original_secret
