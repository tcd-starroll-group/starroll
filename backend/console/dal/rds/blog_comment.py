import logging
from typing import List, Optional

from sqlalchemy import Column, BigInteger, Integer, String, TIMESTAMP, SmallInteger, text
from sqlalchemy.dialects import mysql as _mysql_dialect
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()
logger = logging.getLogger(__name__)


class BlogComment(Base):
    """Blog comment table model"""
    __tablename__ = "blog_comment"

    comment_id = Column(Integer().with_variant(_mysql_dialect.BIGINT(), "mysql"), primary_key=True, autoincrement=True)
    blog_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    content = Column(String(1024), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    is_deleted = Column(SmallInteger, nullable=False, default=0)

    @classmethod
    def create(cls, db: Session, blog_id: int, user_id: int, content: str) -> "BlogComment":
        comment = cls(blog_id=blog_id, user_id=user_id, content=content)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    @classmethod
    def list_by_blog_id(cls, db: Session, blog_id: int) -> List["BlogComment"]:
        return (
            db.query(cls)
            .filter(cls.blog_id == blog_id, cls.is_deleted == 0)
            .order_by(cls.created_at.asc())
            .all()
        )

    @classmethod
    def get_by_id(cls, db: Session, comment_id: int) -> Optional["BlogComment"]:
        return db.query(cls).filter(cls.comment_id == comment_id, cls.is_deleted == 0).first()

    @classmethod
    def soft_delete(cls, db: Session, comment_id: int, user_id: int) -> bool:
        comment = db.query(cls).filter(cls.comment_id == comment_id, cls.user_id == user_id, cls.is_deleted == 0).first()
        if not comment:
            return False
        comment.is_deleted = 1
        db.commit()
        return True