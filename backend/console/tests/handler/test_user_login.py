import asyncio
import hashlib

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import user_login as user_login_module
from backend.console.handler.user_login import api_user_login_post
from backend.console.dal.rds.user import User
from openapi_server.models.user_auth import UserAuth


def test_api_user_login_post_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    raw_password = "password123"
    hashed_password = hashlib.sha256(raw_password.encode()).hexdigest()
    User.create(db_session, "alice", hashed_password, "alice@example.com")

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(user_login_module, "get_db", _get_db_override)

    payload = UserAuth(username="alice", password=raw_password)
    result = asyncio.run(api_user_login_post(payload))

    assert result["message"] == "Login successful"
    assert isinstance(result["token"], str)
    assert result["token"]


def test_api_user_login_post_user_not_found(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(user_login_module, "get_db", _get_db_override)

    payload = UserAuth(username="missing", password="whatever")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_user_login_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_api_user_login_post_password_incorrect(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    hashed_password = hashlib.sha256("correct".encode()).hexdigest()
    User.create(db_session, "bob", hashed_password, "bob@example.com")

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(user_login_module, "get_db", _get_db_override)

    payload = UserAuth(username="bob", password="wrong")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_user_login_post(payload))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Password incorrect"
