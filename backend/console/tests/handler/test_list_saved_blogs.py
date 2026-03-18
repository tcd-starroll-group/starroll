import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import list_saved_blogs as lsb_module


def test_list_saved_blogs_unsupported_sort(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(lsb_module, "auth_module", lsb_module.auth_module)
    monkeypatch.setattr(lsb_module.auth_module,
                        "get_current_user_id", lambda: 1)

    payload = SimpleNamespace(sort="nope", limit=None, offset=None, order=None)
    with pytest.raises(HTTPException):
        asyncio.run(lsb_module.api_list_saved_blogs_post(payload))


def test_list_saved_blogs_success(monkeypatch: pytest.MonkeyPatch):
    class BlogObj(SimpleNamespace):
        pass

    blog1 = BlogObj(blog_id=1, title="a", image_urls=["i1"])
    blog2 = None

    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(lsb_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(lsb_module.auth_module,
                        "get_current_user_id", lambda: 2)
    monkeypatch.setattr(lsb_module.BlogSave, "list_blog_ids_by_user",
                        staticmethod(lambda db, uid, **kw: [1, 2]))
    monkeypatch.setattr(lsb_module.Blog, "get_by_id", staticmethod(
        lambda db, bid: blog1 if bid == 1 else None))

    payload = SimpleNamespace(sort=None, limit=None, offset=None, order=None)
    result = asyncio.run(lsb_module.api_list_saved_blogs_post(payload))
    assert result is not None
