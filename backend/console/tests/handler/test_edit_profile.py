import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import edit_profile as edit_module


def test_edit_profile_invalid_token(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(edit_module, "verify_access_token",
                        lambda t: (None, False))
    payload = SimpleNamespace(username="u", token="bad", profile={})

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(edit_module.api_edit_profile_post(payload))

    assert exc_info.value.status_code == 401


def test_edit_profile_user_not_found(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(edit_module, "verify_access_token",
                        lambda t: ({}, True))

    class Db:
        def query(self, model):
            class Q:
                def filter(self, *a, **kw):
                    class R:
                        def first(self):
                            return None
                    return R()
            return Q()

    class Ctx:
        def __enter__(self):
            return Db()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(edit_module, "db_context", lambda: Ctx())

    payload = SimpleNamespace(username="nouser", token="ok", profile={})
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(edit_module.api_edit_profile_post(payload))

    assert exc_info.value.status_code == 404


def test_edit_profile_success(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(edit_module, "verify_access_token",
                        lambda t: ({"sub": "u"}, True))

    class U:
        id = 5
        email = "test@starroll.com"
        avatar_url = "avatar.png"
        profile = {}

    class Db:
        def query(self, model):
            class Q:
                def filter(self, *a, **kw):
                    class R:
                        def first(self):
                            return U()
                    return R()
            return Q()
        
        # --- THIS IS THE FIX ---
        def commit(self):
            pass
        # -----------------------

    class Ctx:
        def __enter__(self):
            return Db()

        def __exit__(self, *a):
            return False

    edited = {}

    def _edit_profile(db, uid, profile):
        edited["ok"] = True

    monkeypatch.setattr(edit_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(edit_module.User, "get_by_id",
                        staticmethod(lambda db, uid: U()))
    monkeypatch.setattr(edit_module.User, "edit_profile",
                        staticmethod(_edit_profile))

    payload = SimpleNamespace(username="u", token="ok", profile={"email": "new@starroll.com", "avatar": "new.png"})
    result = asyncio.run(edit_module.api_edit_profile_post(payload))
    
    assert (result.get("message") if isinstance(result, dict) else result.message) == "profile updated successfully"
    assert edited.get("ok") is True