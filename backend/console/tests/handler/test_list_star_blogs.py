import asyncio
<<<<<<< HEAD
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import list_star_blogs as list_star_blogs_module
from backend.console.handler.list_star_blogs import api_list_star_blogs_post
from backend.console.dal.rds.blog import Blog
from gen.py.src.openapi_server.models.api_list_blogs_post_request import ApiListBlogsPostRequest


def test_list_star_blogs_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """正常情况：有博客数据，返回该星星下的博客列表"""
    Blog.create(db_session, user_id=1, hip=100, title="Star Blog 1",
                content="content1", image_urls=["http://img1.jpg"])
    Blog.create(db_session, user_id=2, hip=100, title="Star Blog 2",
                content="content2", image_urls=[])
    Blog.create(db_session, user_id=1, hip=999,
                title="Other Star", content="other", image_urls=[])

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_star_blogs_module, "get_db", _get_db_override)

    payload = ApiListBlogsPostRequest(HIP="100")
    result = asyncio.run(api_list_star_blogs_post(payload))

    assert result.blogs_list is not None
    assert len(result.blogs_list) == 2
    titles = [b["title"] for b in result.blogs_list]
    assert "Star Blog 1" in titles
    assert "Star Blog 2" in titles
    assert "Other Star" not in titles


def test_list_star_blogs_empty(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """没有该 HIP 下的博客，返回空列表"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_star_blogs_module, "get_db", _get_db_override)

    payload = ApiListBlogsPostRequest(HIP="999")
    result = asyncio.run(api_list_star_blogs_post(payload))

    assert result.blogs_list == []


def test_list_star_blogs_missing_hip(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """不传 HIP，返回 400"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_star_blogs_module, "get_db", _get_db_override)

    payload = ApiListBlogsPostRequest()
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_list_star_blogs_post(payload))

    assert exc_info.value.status_code == 400
    assert "HIP" in exc_info.value.detail


def test_list_star_blogs_preview_fields(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """确认返回的每个 blogPreview 有正确的字段"""
    Blog.create(db_session, user_id=1, hip=200, title="Field Test",
                content="c", image_urls=["http://img.jpg"])

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_star_blogs_module, "get_db", _get_db_override)

    payload = ApiListBlogsPostRequest(HIP="200")
    result = asyncio.run(api_list_star_blogs_post(payload))

    assert len(result.blogs_list) == 1
    preview = result.blogs_list[0]
    assert "blogID" in preview
    assert preview["title"] == "Field Test"
    assert preview["imageURL"] == "http://img.jpg"


def test_list_star_blogs_excludes_deleted(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """软删除的博客不应该出现在列表里"""
    blog = Blog.create(db_session, user_id=1, hip=300,
                       title="Deleted Blog", content="c", image_urls=[])
    Blog.soft_delete(db_session, blog.blog_id, user_id=1)

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_star_blogs_module, "get_db", _get_db_override)

    payload = ApiListBlogsPostRequest(HIP="300")
    result = asyncio.run(api_list_star_blogs_post(payload))

    assert result.blogs_list == []
=======
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
>>>>>>> main
