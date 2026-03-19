import asyncio
<<<<<<< HEAD
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import list_saved_blogs as list_saved_blogs_module
from backend.console.handler.list_saved_blogs import api_list_saved_blogs_post
from backend.console.dal.rds.blog import Blog
from backend.console.dal.rds.blog_interactions import BlogSave
from gen.py.src.openapi_server.models.api_get_saved_blogs_post_request import ApiGetSavedBlogsPostRequest
from gen.py.src.openapi_server.models.user_credentials import UserCredentials

import backend.console.utils.auth as auth_module


def _make_request(user_id: str, token: str = "valid_token") -> ApiGetSavedBlogsPostRequest:
    return ApiGetSavedBlogsPostRequest(
        userCredentials=UserCredentials(userID=user_id, token=token)
    )


def test_list_saved_blogs_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """正常情况：返回用户收藏的所有博客"""
    blog1 = Blog.create(db_session, user_id=99, hip=1, title="Saved Blog 1",
                        content="c", image_urls=["http://img1.jpg"])
    blog2 = Blog.create(db_session, user_id=99, hip=1,
                        title="Saved Blog 2", content="c", image_urls=[])
    Blog.create(db_session, user_id=99, hip=1,
                title="Not Saved", content="c", image_urls=[])

    BlogSave.create(db_session, blog_id=blog1.blog_id, user_id=1)
    BlogSave.create(db_session, blog_id=blog2.blog_id, user_id=1)

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_saved_blogs_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token",
                        lambda token, user_id: None)

    result = asyncio.run(api_list_saved_blogs_post(_make_request("1")))

    assert len(result.blogs_list) == 2
    titles = [b["title"] for b in result.blogs_list]
    assert "Saved Blog 1" in titles
    assert "Saved Blog 2" in titles
    assert "Not Saved" not in titles


def test_list_saved_blogs_empty(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """该用户没有收藏，返回空列表"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_saved_blogs_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token",
                        lambda token, user_id: None)

    result = asyncio.run(api_list_saved_blogs_post(_make_request("999")))

    assert result.blogs_list == []


def test_list_saved_blogs_missing_credentials(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """不传 userCredentials，返回 400"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_saved_blogs_module, "get_db", _get_db_override)

    payload = ApiGetSavedBlogsPostRequest()
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_list_saved_blogs_post(payload))

    assert exc_info.value.status_code == 400


def test_list_saved_blogs_no_blog_id_needed(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """确认即使传了 blogID 也不影响结果（blogID 已被忽略）"""
    blog = Blog.create(db_session, user_id=99, hip=1,
                       title="Saved", content="c", image_urls=[])
    BlogSave.create(db_session, blog_id=blog.blog_id, user_id=2)

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_saved_blogs_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token",
                        lambda token, user_id: None)

    payload = ApiGetSavedBlogsPostRequest(
        userCredentials=UserCredentials(userID="2", token="t"),
        blogID="12345"
    )
    result = asyncio.run(api_list_saved_blogs_post(payload))

    assert len(result.blogs_list) == 1
    assert result.blogs_list[0]["title"] == "Saved"
=======
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
>>>>>>> main
