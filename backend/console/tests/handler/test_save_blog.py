# Simple, minimal tests for save_blog handler to increase coverage.
import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import save_blog as save_blog_module


def test_save_blog_missing_blog_id_raises_400():
    payload = SimpleNamespace(blog_id="")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(save_blog_module.api_save_blog_post(payload))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "blogID is required"


def test_save_blog_not_found_raises_404(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(save_blog_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(save_blog_module, "auth_module",
                        save_blog_module.auth_module)
    monkeypatch.setattr(save_blog_module.auth_module,
                        "get_current_user_id", lambda: 1)
    monkeypatch.setattr(save_blog_module.Blog, "get_by_id",
                        staticmethod(lambda db, blog_id: None))

    payload = SimpleNamespace(blog_id="101")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(save_blog_module.api_save_blog_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Blog not found"


def test_save_blog_create_and_return_blogid(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    created = {}

    blog_obj = SimpleNamespace(blog_id=5)

    monkeypatch.setattr(save_blog_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(save_blog_module.auth_module,
                        "get_current_user_id", lambda: 42)
    monkeypatch.setattr(save_blog_module.Blog, "get_by_id",
                        staticmethod(lambda db, blog_id: blog_obj))

    def _exists(db, blog_id, user_id):
        return False

    def _create(db, blog_id, user_id):
        created["called"] = True

    monkeypatch.setattr(save_blog_module.BlogSave,
                        "exists", staticmethod(_exists))
    monkeypatch.setattr(save_blog_module.BlogSave,
                        "create", staticmethod(_create))

    payload = SimpleNamespace(blog_id="5")
    result = asyncio.run(save_blog_module.api_save_blog_post(payload))

    assert result.blog_id == "5"
    assert created.get("called") is True


def test_save_blog_already_saved_no_error(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    blog_obj = SimpleNamespace(blog_id=8)

    monkeypatch.setattr(save_blog_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(save_blog_module.auth_module,
                        "get_current_user_id", lambda: 7)
    monkeypatch.setattr(save_blog_module.Blog, "get_by_id",
                        staticmethod(lambda db, blog_id: blog_obj))
    monkeypatch.setattr(save_blog_module.BlogSave, "exists",
                        staticmethod(lambda db, blog_id, user_id: True))

    payload = SimpleNamespace(blog_id="8")
    result = asyncio.run(save_blog_module.api_save_blog_post(payload))

    assert result.blog_id == "8"
