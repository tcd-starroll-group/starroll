import asyncio
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.console.handler import report_blog as report_blog_module
from backend.console.handler.report_blog import api_report_blog_post
from backend.console.dal.rds.blog import Blog, Base as BlogBase
from backend.console.dal.rds.blog_interactions import BlogReport, Base as InteractionBase
from backend.console.dal.rds.blog_comment import Base as CommentBase
from gen.py.src.openapi_server.models.api_get_saved_blogs_post_request import ApiGetSavedBlogsPostRequest
from gen.py.src.openapi_server.models.user_credentials import UserCredentials

import backend.console.utils.auth as auth_module


@pytest.fixture()
def db_session():
    """Local fixture: bypass conftest SQL parsing, use ORM to create tables directly."""
    engine = create_engine("sqlite:///:memory:")
    BlogBase.metadata.create_all(engine)
    InteractionBase.metadata.create_all(engine)
    CommentBase.metadata.create_all(engine)
    LocalSession = sessionmaker(bind=engine)
    session = LocalSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _make_request(user_id: str, blog_id: str, reason: str = "") -> ApiGetSavedBlogsPostRequest:
    req = ApiGetSavedBlogsPostRequest(
        userCredentials=UserCredentials(userID=user_id, token="valid_token"),
        blogID=blog_id
    )
    if reason:
        object.__setattr__(req, "reason", reason)
    return req


def test_report_blog_success_with_reason(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """正常举报，携带 reason"""
    blog = Blog.create(db_session, user_id=99, hip=1, title="Bad Blog", content="bad", image_urls=[])

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(report_blog_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token", lambda token, user_id: None)

    req = _make_request("1", str(blog.blog_id), reason="spam content")
    result = asyncio.run(api_report_blog_post(req))

    assert result.blog_id == str(blog.blog_id)

    report = db_session.query(BlogReport).filter(
        BlogReport.blog_id == blog.blog_id,
        BlogReport.user_id == 1
    ).first()
    assert report is not None
    assert report.reason == "spam content"


def test_report_blog_success_without_reason(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """举报不填 reason，也能成功"""
    blog = Blog.create(db_session, user_id=99, hip=1, title="Blog", content="c", image_urls=[])

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(report_blog_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token", lambda token, user_id: None)

    req = ApiGetSavedBlogsPostRequest(
        userCredentials=UserCredentials(userID="2", token="t"),
        blogID=str(blog.blog_id)
    )
    result = asyncio.run(api_report_blog_post(req))

    assert result.blog_id == str(blog.blog_id)


def test_report_blog_duplicate(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """重复举报同一篇博客，幂等处理不报错"""
    blog = Blog.create(db_session, user_id=99, hip=1, title="Blog", content="c", image_urls=[])
    BlogReport.create(db_session, blog_id=blog.blog_id, user_id=3, reason="first report")

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(report_blog_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token", lambda token, user_id: None)

    req = _make_request("3", str(blog.blog_id), reason="second report")
    result = asyncio.run(api_report_blog_post(req))
    assert result.blog_id == str(blog.blog_id)

    count = db_session.query(BlogReport).filter(
        BlogReport.blog_id == blog.blog_id,
        BlogReport.user_id == 3
    ).count()
    assert count == 1


def test_report_blog_not_found(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """举报不存在的博客，返回 404"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(report_blog_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token", lambda token, user_id: None)

    req = _make_request("1", "99999")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_report_blog_post(req))

    assert exc_info.value.status_code == 404


def test_report_blog_missing_credentials(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """不传 userCredentials，返回 400"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(report_blog_module, "get_db", _get_db_override)

    payload = ApiGetSavedBlogsPostRequest(blogID="1")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_report_blog_post(payload))

    assert exc_info.value.status_code == 400


def test_report_blog_missing_blog_id(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """不传 blogID，返回 400"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(report_blog_module, "get_db", _get_db_override)
    monkeypatch.setattr(auth_module, "verify_user_id_and_token", lambda token, user_id: None)

    payload = ApiGetSavedBlogsPostRequest(
        userCredentials=UserCredentials(userID="1", token="t")
    )
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_report_blog_post(payload))

    assert exc_info.value.status_code == 400