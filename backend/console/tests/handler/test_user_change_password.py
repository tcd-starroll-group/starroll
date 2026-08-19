import asyncio
import hashlib
from contextlib import contextmanager

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import user_change_password as user_change_password_module
from backend.console.handler.user_change_password import api_change_password_post
from backend.console.dal.rds.user import User
from openapi_server.models.change_password_request import ChangePasswordRequest


def test_api_change_password_post_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):

    username = "cp_user"
    old_raw_pass = "old_pass_123"
    new_raw_pass = "new_pass_456"
    old_hashed = hashlib.sha256(old_raw_pass.encode()).hexdigest()

    created = User.create(db_session, username, old_hashed, "cp@example.com")

    @contextmanager
    def _db_context_override():
        yield db_session

    monkeypatch.setattr(user_change_password_module,
                        "db_context", _db_context_override)

    payload = ChangePasswordRequest(
        username=username,
        old_password=old_raw_pass,
        new_password=new_raw_pass
    )

    result = asyncio.run(api_change_password_post(payload))

    assert result["message"] == "Password updated successfully"

    user_in_db = User.get_by_id(db_session, created.id)
    new_expected_hash = hashlib.sha256(new_raw_pass.encode()).hexdigest()
    assert user_in_db.password == new_expected_hash


def test_api_change_password_post_wrong_old_password(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    username = "cp_wrong"
    real_pass = "correct_one"
    real_hashed = hashlib.sha256(real_pass.encode()).hexdigest()
    User.create(db_session, username, real_hashed, "wrong@example.com")

    @contextmanager
    def _db_context_override():
        yield db_session

    monkeypatch.setattr(user_change_password_module,
                        "db_context", _db_context_override)

    payload = ChangePasswordRequest(
        username=username,
        old_password="wrong_input",
        new_password="new_pass"
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_change_password_post(payload))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Old password incorrect"


def test_api_change_password_post_user_not_found(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    @contextmanager
    def _db_context_override():
        yield db_session

    monkeypatch.setattr(user_change_password_module,
                        "db_context", _db_context_override)

    payload = ChangePasswordRequest(
        username="ghost",
        old_password="any",
        new_password="any"
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_change_password_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
