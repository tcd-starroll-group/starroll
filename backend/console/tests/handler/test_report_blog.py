import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import report_blog as report_module


def test_report_blog_missing_raises_400():
    payload = SimpleNamespace(blog_id="")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(report_module.api_report_blog_post(payload))

    assert exc_info.value.status_code == 400


def test_report_blog_not_found(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(report_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(report_module, "auth_module",
                        report_module.auth_module)
    monkeypatch.setattr(report_module.auth_module,
                        "get_current_user_id", lambda: 1)
    monkeypatch.setattr(report_module.Blog, "get_by_id",
                        staticmethod(lambda db, bid: None))

    payload = SimpleNamespace(blog_id="9")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(report_module.api_report_blog_post(payload))

    assert exc_info.value.status_code == 404


def test_report_blog_success_creates(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(report_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(report_module.auth_module,
                        "get_current_user_id", lambda: 2)
    blog_obj = SimpleNamespace(blog_id=3)
    monkeypatch.setattr(report_module.Blog, "get_by_id",
                        staticmethod(lambda db, bid: blog_obj))

    created = {}

    def _exists(db, blog_id, user_id):
        return False

    def _create(*args, **kwargs):
        created.update(kwargs)
        return None

    monkeypatch.setattr(report_module.BlogReport,
                        "exists", staticmethod(_exists))
    monkeypatch.setattr(report_module.BlogReport,
                        "create", staticmethod(_create))

    payload = SimpleNamespace(blog_id="3", reason="spam")
    result = asyncio.run(report_module.api_report_blog_post(payload))

    assert result.blog_id == "3"
