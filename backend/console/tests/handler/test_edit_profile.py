import asyncio
import hashlib

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import edit_profile as edit_profile_module
from backend.console.handler.edit_profile import api_edit_profile_post
from backend.console.dal.rds.user import User
from gen.py.src.openapi_server.models.profile_and_token import ProfileAndToken


def test_api_edit_profile_post_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    # Create a user so that User.get_by_username will succeed
    raw_password = "password123"
    hashed_password = hashlib.sha256(raw_password.encode()).hexdigest()
    User.create(db_session, "alice", hashed_password, "alice@example.com")

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(edit_profile_module, "get_db", _get_db_override)

    # Mock token verification (must return (payload, is_valid))
    def mock_verify_access_token(token):
        return {"sub": "alice"}, True

    monkeypatch.setattr(edit_profile_module, "verify_access_token", mock_verify_access_token)

    # Profile payload – the exact shape depends on the generated model,
    # but a dict is the most common for a free-form profile update.
    profile = {
        "email": "newemail@example.com",
        "bio": "Updated bio",
        "avatar_url": "https://example.com/new-avatar.jpg"
    }

    payload = ProfileAndToken(
        username="alice",
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy",
        profile=profile
    )

    result = asyncio.run(api_edit_profile_post(payload))

    assert result["message"] == "profile updated successfully"


def test_api_edit_profile_post_token_invalid(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(edit_profile_module, "get_db", _get_db_override)

    def mock_verify_access_token(token):
        return None, False

    monkeypatch.setattr(edit_profile_module, "verify_access_token", mock_verify_access_token)

    payload = ProfileAndToken(
        username="alice",
        token="invalid.token.here",
        profile={}
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_edit_profile_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "token invalid"


def test_api_edit_profile_post_user_not_found(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(edit_profile_module, "get_db", _get_db_override)

    def mock_verify_access_token(token):
        return {"sub": "alice"}, True

    monkeypatch.setattr(edit_profile_module, "verify_access_token", mock_verify_access_token)

    payload = ProfileAndToken(
        username="missing_user",
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.valid",
        profile={}
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_edit_profile_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"