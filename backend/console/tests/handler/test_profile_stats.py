from types import SimpleNamespace

import asyncio
import pytest
from fastapi import HTTPException

from backend.console.handler import profile_stats as ps_module


def test_profile_stats_user_not_found(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(ps_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(ps_module, "get_current_user_id", lambda: 999)
    monkeypatch.setattr(ps_module.UserDAL, "get_by_id",
                        staticmethod(lambda db, uid: None))

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(ps_module.api_get_profile_stats_post(None))

    assert exc_info.value.status_code == 404


def test_profile_stats_success(monkeypatch: pytest.MonkeyPatch):
    created_at = None
    
    # FIX: Added email, avatar_url, and profile to the fake database record
    user = SimpleNamespace(
        is_deleted=False, 
        created_at=created_at,
        email="test@starroll.com",
        avatar_url="avatar.png",
        profile={}
    )

    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(ps_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(ps_module, "get_current_user_id", lambda: 1)
    monkeypatch.setattr(ps_module.UserDAL, "get_by_id",
                        staticmethod(lambda db, uid: user))
    monkeypatch.setattr(ps_module.IdentifyStarsJobDAL,
                        "count_all_time_scans", staticmethod(lambda db, uid: 7))
    monkeypatch.setattr(ps_module.UserDiscoveredStarsDAL,
                        "count_user_discoveries", staticmethod(lambda db, uid: 60))

    result = asyncio.run(ps_module.api_get_profile_stats_post(None))

    # Handles both dict returns and Pydantic object returns just in case
    if isinstance(result, dict):
        assert result["starsDiscovered"] == 60
        assert result["totalScans"] == 7
        assert result["rank"] == "Astronomer"
    else:
        assert result.stars_discovered == 60
        assert result.total_scans == 7
        assert result.rank == "Astronomer"