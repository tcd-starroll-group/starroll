import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import discover_star as discover_star_module


def test_discover_star_missing_hip_raises_400():
    """Request with no hip field should raise 400."""
    payload = SimpleNamespace(hip=None)
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(discover_star_module.api_discover_star_post(payload))
    assert exc_info.value.status_code == 400


def test_discover_star_none_request_raises_400():
    """None request should raise 400."""
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(discover_star_module.api_discover_star_post(None))
    assert exc_info.value.status_code == 400


def test_discover_star_creates_record_when_not_exists(monkeypatch: pytest.MonkeyPatch):
    """Should call UserDiscoveredStars.create when the record does not exist."""

    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    created = {}

    monkeypatch.setattr(discover_star_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(discover_star_module.auth_module,
                        "get_current_user_id", lambda: "99")
    monkeypatch.setattr(discover_star_module.UserDiscoveredStars,
                        "exists", staticmethod(lambda db, user_id, hip_id: False))
    monkeypatch.setattr(discover_star_module.UserDiscoveredStars,
                        "create", staticmethod(lambda db, user_id, hip_id: created.update({"user_id": user_id, "hip_id": hip_id})))

    payload = SimpleNamespace(hip=12345)
    result = asyncio.run(discover_star_module.api_discover_star_post(payload))

    assert result.message == "ok"
    assert created["user_id"] == 99
    assert created["hip_id"] == 12345


def test_discover_star_skips_create_when_already_exists(monkeypatch: pytest.MonkeyPatch):
    """Should not call create when record already exists."""

    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    created = {}

    monkeypatch.setattr(discover_star_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(discover_star_module.auth_module,
                        "get_current_user_id", lambda: "99")
    monkeypatch.setattr(discover_star_module.UserDiscoveredStars,
                        "exists", staticmethod(lambda db, user_id, hip_id: True))
    monkeypatch.setattr(discover_star_module.UserDiscoveredStars,
                        "create", staticmethod(lambda db, user_id, hip_id: created.update({"called": True})))

    payload = SimpleNamespace(hip=12345)
    result = asyncio.run(discover_star_module.api_discover_star_post(payload))

    assert result.message == "ok"
    assert "called" not in created
