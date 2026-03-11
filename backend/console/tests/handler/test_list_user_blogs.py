import asyncio
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import list_user_blogs as list_user_blogs_module
from backend.console.handler.list_user_blogs import api_list_user_blogs_post
from backend.console.dal.rds.blog import Blog
from gen.py.src.openapi_server.models.api_get_saved_blogs_post_request import ApiGetSavedBlogsPostRequest
from gen.py.src.openapi_server.models.user_credentials import UserCredentials

import backend.console.utils.auth as auth_module


def _make_request(user_id: str, token: str = "valid_token") -> ApiGetSavedBlogsPostRequest:
    return ApiGetSavedBlogsPostRequest(
        userCredentials=UserCredentials(userID=user_id, token=token)
    )


def test_list_user_blogs_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """正常情况：返回该用户发的所有博客"""
    Blog.create(db_session, user_id=1, hip=100, title="My Blog 1",
                content="c1", image_urls=["http://img1.jpg"])
    Blog.create(db_session, user_id=1, hip=200,
                title="My Blog 2", content="c2", image_urls=[])
    Blog.create(db_session, user_id=2, hip=100,
                title="Other User Blog", content="c3", image_urls=[])

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_user_blogs_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token",
                        lambda token, user_id: None)

    result = asyncio.run(api_list_user_blogs_post(_make_request("1")))

    assert len(result.blogs_list) == 2
    titles = [b["title"] for b in result.blogs_list]
    assert "My Blog 1" in titles
    assert "My Blog 2" in titles
    assert "Other User Blog" not in titles


def test_list_user_blogs_empty(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """该用户没有发过博客，返回空列表"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_user_blogs_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token",
                        lambda token, user_id: None)

    result = asyncio.run(api_list_user_blogs_post(_make_request("999")))

    assert result.blogs_list == []


def test_list_user_blogs_missing_credentials(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """不传 userCredentials，返回 400"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_user_blogs_module, "get_db", _get_db_override)

    payload = ApiGetSavedBlogsPostRequest()
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_list_user_blogs_post(payload))

    assert exc_info.value.status_code == 400


def test_list_user_blogs_excludes_deleted(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """软删除的博客不出现"""
    blog = Blog.create(db_session, user_id=5, hip=100,
                       title="To Delete", content="c", image_urls=[])
    Blog.create(db_session, user_id=5, hip=100,
                title="Active Blog", content="c", image_urls=[])
    Blog.soft_delete(db_session, blog.blog_id, user_id=5)

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(list_user_blogs_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token",
                        lambda token, user_id: None)

    result = asyncio.run(api_list_user_blogs_post(_make_request("5")))

    assert len(result.blogs_list) == 1
    assert result.blogs_list[0]["title"] == "Active Blog"
