import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import like_blog as like_module


def test_like_blog_missing_raises_400():
    payload = SimpleNamespace(blog_id="")
    with pytest.raises(HTTPException):
        asyncio.run(like_module.api_like_blog_post(payload))


def test_like_blog_not_found(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(like_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(like_module.auth_module,
                        "get_current_user_id", lambda: 1)
    monkeypatch.setattr(like_module.Blog, "get_by_id",
                        staticmethod(lambda db, bid: None))

    payload = SimpleNamespace(blog_id="9")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(like_module.api_like_blog_post(payload))

    assert exc_info.value.status_code == 404


def test_like_blog_success(monkeypatch: pytest.MonkeyPatch):
    class Db:
        def refresh(self, obj):
            return None

    class Ctx:
        def __enter__(self):
            return Db()

        def __exit__(self, *a):
            return False

    blog = SimpleNamespace(blog_id=4, like_count=3)

    monkeypatch.setattr(like_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(like_module.auth_module,
                        "get_current_user_id", lambda: 7)
    monkeypatch.setattr(like_module.Blog, "get_by_id",
                        staticmethod(lambda db, bid: blog))

    def _exists(db, blog_id, user_id):
        return False

    def _create(*args, **kwargs):
        return None

    def _increment_like_count(db, bid):
        setattr(blog, "like_count", 10)

    monkeypatch.setattr(like_module.BlogLike, "exists",
                        staticmethod(_exists))
    monkeypatch.setattr(like_module.BlogLike, "create",
                        staticmethod(_create))
    monkeypatch.setattr(
        like_module.Blog, "increment_like_count", staticmethod(_increment_like_count))

    payload = SimpleNamespace(blog_id="4")
    result = asyncio.run(like_module.api_like_blog_post(payload))
    assert result.blog_id == "4"
    assert result.like_number == 10
