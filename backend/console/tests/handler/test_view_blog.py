import asyncio
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.console.handler import view_blog as view_blog_module
from backend.console.handler.view_blog import api_view_blog_post
from backend.console.dal.rds.blog import Blog, Base as BlogBase
from backend.console.dal.rds.blog_interactions import Base as InteractionBase
from backend.console.dal.rds.blog_comment import BlogComment, Base as CommentBase
from gen.py.src.openapi_server.models.api_view_blog_post_request import ApiViewBlogPostRequest


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


def test_view_blog_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """正常情况：用 blogID 查到博客，返回完整信息"""
    blog = Blog.create(db_session, user_id=1, hip=100, title="View Test", content="Hello World", image_urls=["http://img.jpg"])

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(view_blog_module, "get_db", _get_db_override)

    payload = ApiViewBlogPostRequest(blogID=str(blog.blog_id))
    result = asyncio.run(api_view_blog_post(payload))

    assert result.blog_id == str(blog.blog_id)
    assert result.title == "View Test"
    assert result.content == "Hello World"
    assert result.image_url_list == ["http://img.jpg"]
    assert result.like_number == 0
    assert result.comment_number == 0


def test_view_blog_with_comments(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """有评论的博客，返回评论列表"""
    blog = Blog.create(db_session, user_id=1, hip=100, title="Blog With Comments", content="c", image_urls=[])
    BlogComment.create(db_session, blog_id=blog.blog_id, user_id=2, content="Great post!")
    BlogComment.create(db_session, blog_id=blog.blog_id, user_id=3, content="Nice!")
    Blog.increment_comment_count(db_session, blog.blog_id)
    Blog.increment_comment_count(db_session, blog.blog_id)

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(view_blog_module, "get_db", _get_db_override)

    payload = ApiViewBlogPostRequest(blogID=str(blog.blog_id))
    result = asyncio.run(api_view_blog_post(payload))

    assert result.comment_number == 2
    assert len(result.comment_list) == 2
    texts = [c.comment_text for c in result.comment_list]
    assert "Great post!" in texts
    assert "Nice!" in texts


def test_view_blog_not_found(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """博客不存在，返回 404"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(view_blog_module, "get_db", _get_db_override)

    payload = ApiViewBlogPostRequest(blogID="99999")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_view_blog_post(payload))

    assert exc_info.value.status_code == 404


def test_view_blog_missing_blog_id(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """不传 blogID，返回 400"""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(view_blog_module, "get_db", _get_db_override)

    payload = ApiViewBlogPostRequest()
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_view_blog_post(payload))

    assert exc_info.value.status_code == 400
    assert "blogID" in exc_info.value.detail


def test_view_blog_deleted_returns_404(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """软删除的博客，返回 404"""
    blog = Blog.create(db_session, user_id=1, hip=100, title="Deleted", content="c", image_urls=[])
    Blog.soft_delete(db_session, blog.blog_id, user_id=1)

    def _get_db_override():
        yield db_session

    monkeypatch.setattr(view_blog_module, "get_db", _get_db_override)

    payload = ApiViewBlogPostRequest(blogID=str(blog.blog_id))
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_view_blog_post(payload))

    assert exc_info.value.status_code == 404