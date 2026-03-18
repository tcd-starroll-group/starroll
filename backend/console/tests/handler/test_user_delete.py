import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import user_delete as user_delete_module


def test_api_delete_user_post_not_found(monkeypatch: pytest.MonkeyPatch):
    called = {}

    class Db:
        def rollback(self):
            called["rollback"] = True

    class Ctx:
        def __enter__(self):
            return Db()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(user_delete_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(user_delete_module, "get_current_user_id", lambda: 123)
    monkeypatch.setattr(user_delete_module.User, "get_by_id",
                        staticmethod(lambda db, uid: None))

    payload = SimpleNamespace(username="noname")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(user_delete_module.api_delete_user_post(payload))

    assert exc_info.value.status_code == 404
    assert called.get("rollback") is True


def test_api_delete_user_post_success(monkeypatch: pytest.MonkeyPatch):
    called = {}

    class Db:
        def rollback(self):
            called["rollback"] = True

    class Ctx:
        def __enter__(self):
            return Db()

        def __exit__(self, *a):
            return False

    def _delete_by_id(db, uid):
        called["deleted_id"] = uid

    monkeypatch.setattr(user_delete_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(user_delete_module, "get_current_user_id", lambda: 55)
    monkeypatch.setattr(user_delete_module.User, "get_by_id",
                        staticmethod(lambda db, uid: SimpleNamespace(id=55)))
    monkeypatch.setattr(user_delete_module.User,
                        "delete_by_id", staticmethod(_delete_by_id))

    payload = SimpleNamespace(username="me")
    result = asyncio.run(user_delete_module.api_delete_user_post(payload))

    assert result.message == "Account deleted successfully"
    assert called.get("deleted_id") == 55
