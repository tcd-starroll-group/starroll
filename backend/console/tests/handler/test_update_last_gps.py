import asyncio
import hashlib

import pytest
from fastapi import HTTPException

from backend.console.dal.rds.user import User
from backend.console.handler import update_last_gps as update_last_gps_module
from backend.console.handler.update_last_gps import api_update_last_gps_post
from gen.py.src.openapi_server.models.api_update_last_gps_post_request import ApiUpdateLastGpsPostRequest
from gen.py.src.openapi_server.models.gps import GPS


def test_api_update_last_gps_post_success(db_session, monkeypatch):
    hashed_password = hashlib.sha256("password123".encode()).hexdigest()
    User.create(db_session, "alice", hashed_password, "alice@example.com")

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(update_last_gps_module, "get_db", _get_db_override)
    monkeypatch.setattr(
        update_last_gps_module,
        "verify_access_token",
        lambda token: ({"sub": "alice"}, True),
    )

    payload = ApiUpdateLastGpsPostRequest(
        username="alice",
        token="valid.token",
        gps=GPS(latitude=30.2741, longitude=120.1551),
    )

    result = asyncio.run(api_update_last_gps_post(payload))

    assert result["message"] == "last gps updated successfully"
    user = User.get_by_username(db_session, "alice")
    assert user.last_gps == {"longitude": 120.1551, "latitude": 30.2741}


def test_api_update_last_gps_post_token_invalid(db_session, monkeypatch):
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(update_last_gps_module, "get_db", _get_db_override)
    monkeypatch.setattr(
        update_last_gps_module,
        "verify_access_token",
        lambda token: (None, False),
    )

    payload = ApiUpdateLastGpsPostRequest(
        username="alice",
        token="invalid.token",
        gps=GPS(latitude=30.2741, longitude=120.1551),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_update_last_gps_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "token invalid"


def test_api_update_last_gps_post_user_not_found(db_session, monkeypatch):
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(update_last_gps_module, "get_db", _get_db_override)
    monkeypatch.setattr(
        update_last_gps_module,
        "verify_access_token",
        lambda token: ({"sub": "missing_user"}, True),
    )

    payload = ApiUpdateLastGpsPostRequest(
        username="missing_user",
        token="valid.token",
        gps=GPS(latitude=30.2741, longitude=120.1551),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_update_last_gps_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
