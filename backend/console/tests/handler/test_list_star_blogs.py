import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import list_star_blogs as lsb_module


def test_list_star_blogs_missing_hip_raises_400():
    payload = SimpleNamespace(hip=None)
    with pytest.raises(HTTPException):
        asyncio.run(lsb_module.api_list_star_blogs_post(payload))


def test_list_star_blogs_success(monkeypatch: pytest.MonkeyPatch):
    class BlogObj(SimpleNamespace):
        pass

    blogs = [BlogObj(blog_id=10, title="x", image_urls=["a"])]

    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(lsb_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(lsb_module.Blog, "list_by_hip",
                        staticmethod(lambda db, hip, **kw: blogs))

    payload = SimpleNamespace(hip="42", limit=None,
                              offset=None, sort=None, order=None)
    result = asyncio.run(lsb_module.api_list_star_blogs_post(payload))
    assert hasattr(result, "blogs_list")
