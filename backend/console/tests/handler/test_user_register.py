import asyncio
import hashlib

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import user_register as user_register_module
from backend.console.handler.user_register import api_user_reg_post
from backend.console.dal.rds.user import User
from gen.py.src.openapi_server.models.api_user_reg_post_request import ApiUserRegPostRequest


def test_api_user_reg_post_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(user_register_module, "get_db", _get_db_override)

    payload = ApiUserRegPostRequest(
        username="newuser",
        password="password123",
        email="new@example.com"
    )
    
    result = asyncio.run(api_user_reg_post(payload))

    assert result.username == "newuser"
    
    assert result.user_id is not None
    assert result.user_id.isdigit()

    user_in_db = User.get_by_username(db_session, "newuser")
    assert user_in_db is not None
    assert user_in_db.email == "new@example.com"

    expected_hash = hashlib.sha256("password123".encode()).hexdigest()
    assert user_in_db.password == expected_hash


def test_api_user_reg_post_duplicate_username(db_session: Session, monkeypatch: pytest.MonkeyPatch):

    existing_password = hashlib.sha256("pwd".encode()).hexdigest()
    User.create(db_session, "duplicate_user", existing_password, "u1@example.com")

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(user_register_module, "get_db", _get_db_override)

    payload = ApiUserRegPostRequest(
        username="duplicate_user",
        password="password456",
        email="u2@example.com"
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_user_reg_post(payload))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Username already exists"