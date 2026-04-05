import datetime
import time

import jwt
import pytest
from fastapi import HTTPException

from backend.console.utils.auth import create_access_token, verify_access_token, verify_user_id_and_token
from backend.config import settings


class TestCreateAccessToken:
    def test_create_access_token_success(self):
        """Test successful token creation with valid data."""
        data = {"user_name": "alice", "user_id": 123}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert token  # Token should not be empty

    def test_create_access_token_contains_payload(self):
        """Test that the created token contains the provided data."""
        data = {"user_name": "bob", "user_id": 456}
        token = create_access_token(data)

        # Decode without verification to check payload
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["user_name"] == "bob"
        assert payload["user_id"] == 456
        assert "exp" in payload

    def test_create_access_token_has_expiration(self):
        """Test that the created token has proper expiration time."""
        data = {"user_name": "carol"}
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
        data = {"user_name": "dave", "user_id": 789}
        token = create_access_token(data)

        payload, is_valid = verify_access_token(token)
        assert is_valid is True
        assert payload is not None
        assert payload["user_name"] == "dave"
        assert payload["user_id"] == 789

    def test_verify_access_token_invalid_token(self):
        """Test verification with invalid token format."""
        payload, is_valid = verify_access_token("invalid.token.here")
        assert is_valid is False
        assert payload is None

    def test_verify_access_token_corrupted_signature(self):
        """Test verification with corrupted token signature."""
        data = {"user_name": "eve"}
        token = create_access_token(data)
        # Tamper with the token
        corrupted_token = token[:-10] + "aaaaaaaaaa"

        payload, is_valid = verify_access_token(corrupted_token)
        assert is_valid is False
        assert payload is None

    def test_verify_access_token_expired(self):
        """Test verification with expired token."""
        # Create a token with very short expiration
        data = {"user_name": "frank"}
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
        data = {"user_name": "grace"}
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


class TestVerifyUserIdAndToken:
    """Test cases for verify_user_id_and_token function."""

    def test_verify_user_id_and_token_success(self):
        """Test successful verification with matching user_id."""
        data = {"user_name": "alice", "user_id": 123}
        token = create_access_token(data)

        # Should not raise any exception
        verify_user_id_and_token(token, "123")

    def test_verify_user_id_and_token_success_int_user_id(self):
        """Test successful verification with integer user_id in request."""
        data = {"user_name": "bob", "user_id": 456}
        token = create_access_token(data)

        # Should not raise any exception (both int and str should work)
        verify_user_id_and_token(token, "456")

    def test_verify_user_id_and_token_success_str_user_id_in_token(self):
        """Test successful verification with string user_id in token."""
        data = {"user_name": "carol", "user_id": "789"}
        token = create_access_token(data)

        # Should not raise any exception
        verify_user_id_and_token(token, "789")

    def test_verify_user_id_and_token_invalid_token(self):
        """Test verification with invalid token raises 401."""
        with pytest.raises(HTTPException) as exc_info:
            verify_user_id_and_token("invalid.token.here", "123")

        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in exc_info.value.detail

    def test_verify_user_id_and_token_expired_token(self):
        """Test verification with expired token raises 401."""
        data = {"user_name": "dave", "user_id": 999}
        to_encode = data.copy()
        expire = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(seconds=1)
        to_encode.update({"exp": expire})
        expired_token = jwt.encode(
            to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_user_id_and_token(expired_token, "999")

        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in exc_info.value.detail

    def test_verify_user_id_and_token_mismatched_user_id(self):
        """Test verification with mismatched user_id raises 403."""
        data = {"user_name": "eve", "user_id": 111}
        token = create_access_token(data)

        with pytest.raises(HTTPException) as exc_info:
            verify_user_id_and_token(token, "222")

        assert exc_info.value.status_code == 403
        assert "User ID mismatch" in exc_info.value.detail

    def test_verify_user_id_and_token_missing_user_id_in_token(self):
        """Test verification with token missing user_id raises 403."""
        data = {"user_name": "frank"}  # No user_id in payload
        token = create_access_token(data)

        with pytest.raises(HTTPException) as exc_info:
            verify_user_id_and_token(token, "123")

        assert exc_info.value.status_code == 403
        assert "User ID mismatch" in exc_info.value.detail

    def test_verify_user_id_and_token_none_user_id_in_token(self):
        """Test verification with None user_id in token raises 403."""
        data = {"user_name": "grace", "user_id": None}
        token = create_access_token(data)

        with pytest.raises(HTTPException) as exc_info:
            verify_user_id_and_token(token, "123")

        assert exc_info.value.status_code == 403
        assert "User ID mismatch" in exc_info.value.detail

    def test_verify_user_id_and_token_type_conversion(self):
        """Test that the function properly handles type conversion for comparison."""
        # Token has integer user_id
        data = {"user_name": "henry", "user_id": 555}
        token = create_access_token(data)

        # Request has string user_id - should match due to str() conversion
        verify_user_id_and_token(token, "555")

        # This should also work
        data2 = {"user_name": "iris", "user_id": "666"}
        token2 = create_access_token(data2)
        verify_user_id_and_token(token2, "666")
