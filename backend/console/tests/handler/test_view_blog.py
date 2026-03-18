import asyncio
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import view_blog as view_blog_module


def test_view_blog_missing_blog_id_raises_400():
    payload = SimpleNamespace(blog_id="")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(view_blog_module.api_view_blog_post(payload))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "blogID is required"


def test_view_blog_not_found_raises_404(monkeypatch: pytest.MonkeyPatch):
    def _get_db_override():
        yield object()

    monkeypatch.setattr(view_blog_module, "get_db", _get_db_override)
    monkeypatch.setattr(view_blog_module.Blog, "get_by_id",
                        staticmethod(lambda db, blog_id: None))

    payload = SimpleNamespace(blog_id="101")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(view_blog_module.api_view_blog_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Blog not found"


def test_view_blog_success_returns_blog(monkeypatch: pytest.MonkeyPatch):
    def _get_db_override():
        yield object()

    blog_obj = SimpleNamespace(
        blog_id=7,
        title="hello",
        image_urls=["https://img/a.png"],
        content="content",
        comment_count=3,
        like_count=9,
    )
    comment_obj = SimpleNamespace(
        comment_id=11,
        content="nice",
        user_id=22,
        created_at=datetime(2026, 3, 18, 10, 0, 0),
    )

    monkeypatch.setattr(view_blog_module, "get_db", _get_db_override)
    monkeypatch.setattr(view_blog_module.Blog, "get_by_id",
                        staticmethod(lambda db, blog_id: blog_obj))
    monkeypatch.setattr(view_blog_module.BlogComment, "list_by_blog_id",
                        staticmethod(lambda db, blog_id: [comment_obj]))

    payload = SimpleNamespace(blog_id="7")
    result = asyncio.run(view_blog_module.api_view_blog_post(payload))

    assert result.blog_id == "7"
    assert result.title == "hello"
    assert result.image_url_list == ["https://img/a.png"]
    assert result.content == "content"
    assert result.comment_number == 3
    assert result.like_number == 9
    assert len(result.comment_list) == 1
    assert result.comment_list[0].comment_id == "11"
    assert result.comment_list[0].comment_text == "nice"
    assert result.comment_list[0].user_id == "22"
    assert result.comment_list[0].time == "2026-03-18T10:00:00"


def test_view_blog_unexpected_error_raises_500(monkeypatch: pytest.MonkeyPatch):
    def _get_db_override():
        yield object()

    def _raise_error(db, blog_id):
        raise RuntimeError("db exploded")

    monkeypatch.setattr(view_blog_module, "get_db", _get_db_override)
    monkeypatch.setattr(view_blog_module.Blog, "get_by_id",
                        staticmethod(_raise_error))

    payload = SimpleNamespace(blog_id="5")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(view_blog_module.api_view_blog_post(payload))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Failed to retrieve blog"
