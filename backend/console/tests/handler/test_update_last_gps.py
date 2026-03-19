import asyncio
<<<<<<< HEAD
import hashlib
=======
from types import SimpleNamespace
>>>>>>> main

import pytest
from fastapi import HTTPException

<<<<<<< HEAD
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
=======
from backend.console.handler import update_last_gps as update_module


def test_update_last_gps_user_not_found_raises_404(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(update_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(update_module, "get_current_user_id", lambda: 999)
    monkeypatch.setattr(update_module.User, "get_by_id",
                        staticmethod(lambda db, uid: None))

    payload = SimpleNamespace(gps=SimpleNamespace(
        to_dict=lambda: {"lat": 0, "lng": 0}))

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(update_module.api_update_last_gps_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"


def test_update_last_gps_success_calls_set_last_gps(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    called = {}

    def _set_last_gps(db, gps_dict):
        called["gps"] = gps_dict

    user_obj = SimpleNamespace(set_last_gps=_set_last_gps)

    monkeypatch.setattr(update_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(update_module, "get_current_user_id", lambda: 1)
    monkeypatch.setattr(update_module.User, "get_by_id",
                        staticmethod(lambda db, uid: user_obj))

    payload = SimpleNamespace(gps=SimpleNamespace(
        to_dict=lambda: {"lat": 11.1, "lng": 22.2}))
    result = asyncio.run(update_module.api_update_last_gps_post(payload))

    assert isinstance(result, dict)
    assert result.get("message") == "last gps updated successfully"
    assert called.get("gps") == {"lat": 11.1, "lng": 22.2}
>>>>>>> main
