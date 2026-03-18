import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import list_user_blogs as lub_module


def test_list_user_blogs_unsupported_sort_raises_400(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(lub_module, "auth_module", lub_module.auth_module)
    monkeypatch.setattr(lub_module.auth_module,
                        "get_current_user_id", lambda: 1)

    with pytest.raises(HTTPException):
        asyncio.run(lub_module.api_list_user_blogs_post(
            {"sort": "unsupported_field"}))


def test_list_user_blogs_success(monkeypatch: pytest.MonkeyPatch):
    class BlogObj(SimpleNamespace):
        pass

    blogs = [BlogObj(blog_id=1, title="t1", image_urls=["u1"]),
             BlogObj(blog_id=2, title="t2", image_urls=[])]

    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(lub_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(lub_module, "auth_module", lub_module.auth_module)
    monkeypatch.setattr(lub_module.auth_module,
                        "get_current_user_id", lambda: 2)
    monkeypatch.setattr(lub_module.Blog, "list_by_user_id",
                        staticmethod(lambda db, uid, **kw: blogs))

    result = asyncio.run(lub_module.api_list_user_blogs_post(None))
    assert result is not None
