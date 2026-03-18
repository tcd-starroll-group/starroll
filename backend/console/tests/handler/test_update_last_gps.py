import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

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
