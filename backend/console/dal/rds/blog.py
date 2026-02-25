import logging
from typing import List, Optional

from sqlalchemy import Column, BigInteger, Integer, String, Text, JSON, TIMESTAMP, SmallInteger, text
from sqlalchemy.dialects import mysql as _mysql_dialect
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()
logger = logging.getLogger(__name__)


class Blog(Base):
    """Blog table model"""
    __tablename__ = "blog"

    blog_id = Column(Integer().with_variant(_mysql_dialect.BIGINT(), "mysql"), primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    hip = Column(Integer, nullable=False)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=True)
    image_urls = Column(JSON, nullable=True)
    like_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
    is_deleted = Column(SmallInteger, nullable=False, default=0)

    @classmethod
    def create(cls, db: Session, user_id: int, hip: int, title: str, content: str, image_urls: List[str]) -> "Blog":
        new_blog = cls(user_id=user_id, hip=hip, title=title, content=content, image_urls=image_urls or [])
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        return new_blog

    @classmethod
    def get_by_id(cls, db: Session, blog_id: int) -> Optional["Blog"]:
        return db.query(cls).filter(cls.blog_id == blog_id, cls.is_deleted == 0).first()

    @classmethod
    def list_by_hip(cls, db: Session, hip: int) -> List["Blog"]:
        return (
            db.query(cls)
            .filter(cls.hip == hip, cls.is_deleted == 0)
            .order_by(cls.created_at.desc())
            .all()
        )

    @classmethod
    def list_by_user_id(cls, db: Session, user_id: int) -> List["Blog"]:
        return (
            db.query(cls)
            .filter(cls.user_id == user_id, cls.is_deleted == 0)
            .order_by(cls.created_at.desc())
            .all()
        )

    @classmethod
    def soft_delete(cls, db: Session, blog_id: int, user_id: int) -> bool:
        blog = db.query(cls).filter(cls.blog_id == blog_id, cls.user_id == user_id, cls.is_deleted == 0).first()
        if not blog:
            return False
        blog.is_deleted = 1
        db.commit()
        return True

    @classmethod
    def increment_like_count(cls, db: Session, blog_id: int) -> None:
        blog = cls.get_by_id(db, blog_id)
        if blog:
            blog.like_count = (blog.like_count or 0) + 1
            db.commit()

    @classmethod
    def increment_comment_count(cls, db: Session, blog_id: int) -> None:
        blog = cls.get_by_id(db, blog_id)
        if blog:
            blog.comment_count = (blog.comment_count or 0) + 1
            db.commit()

    @classmethod
    def decrement_comment_count(cls, db: Session, blog_id: int) -> None:
        blog = cls.get_by_id(db, blog_id)
        if blog and blog.comment_count > 0:
            blog.comment_count -= 1
            db.commit()