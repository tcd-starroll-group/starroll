import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import delete_blog as del_module


def test_delete_blog_missing_raises_400():
    payload = SimpleNamespace(blog_id="")
    with pytest.raises(HTTPException):
        asyncio.run(del_module.api_delete_blog_post(payload))


def test_delete_blog_not_found(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(del_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(del_module.auth_module,
                        "get_current_user_id", lambda: 1)
    monkeypatch.setattr(del_module.Blog, "soft_delete",
                        staticmethod(lambda db, blog_id, user_id: False))

    payload = SimpleNamespace(blog_id="8")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(del_module.api_delete_blog_post(payload))

    assert exc_info.value.status_code == 404


def test_delete_blog_success(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(del_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(del_module.auth_module,
                        "get_current_user_id", lambda: 2)
    monkeypatch.setattr(del_module.Blog, "soft_delete",
                        staticmethod(lambda db, blog_id, user_id: True))

    payload = SimpleNamespace(blog_id="8")
    result = asyncio.run(del_module.api_delete_blog_post(payload))
    assert result.blog_id == "8"
