import asyncio
import hashlib

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import user_delete as user_delete_module
from backend.console.handler.user_delete import api_delete_user_post
from backend.console.dal.rds.user import User
from gen.py.src.openapi_server.models.user_auth import UserAuth


def test_api_delete_user_post_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    username = "del_user"
    password = "del_password"
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    User.create(db_session, username, hashed, "del@example.com")

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(user_delete_module, "get_db", _get_db_override)

    payload = UserAuth(username=username, password=password)

    result = asyncio.run(api_delete_user_post(payload))

    assert result.message == "Account deleted successfully"

    user_in_db = User.get_by_username(db_session, username)
    assert user_in_db is None


def test_api_delete_user_post_wrong_password(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    username = "safe_user"
    password = "real_password"
    hashed = hashlib.sha256(password.encode()).hexdigest()
    User.create(db_session, username, hashed, "safe@example.com")

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(user_delete_module, "get_db", _get_db_override)

    payload = UserAuth(username=username, password="wrong_password")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_delete_user_post(payload))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Password incorrect"
    
    assert User.get_by_username(db_session, username) is not None


def test_api_delete_user_post_not_found(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(user_delete_module, "get_db", _get_db_override)

    payload = UserAuth(username="missing_user", password="any")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_delete_user_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"