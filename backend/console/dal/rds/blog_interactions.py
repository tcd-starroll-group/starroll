import logging
from typing import List, Optional

from sqlalchemy import Column, BigInteger, Integer, String, TIMESTAMP, text
from sqlalchemy.dialects import mysql as _mysql_dialect
from sqlalchemy.orm import declarative_base, Session
from backend.constant.sort import SORT_BY_CREATE_TIME, SORT_ORDER_DESC, SORT_ORDER_ASC

Base = declarative_base()
logger = logging.getLogger(__name__)


# -------------------------------------------------------
# Blog Like
# -------------------------------------------------------

class BlogLike(Base):
    __tablename__ = "blog_like"

    like_id = Column(Integer().with_variant(
        _mysql_dialect.BIGINT(), "mysql"), primary_key=True, autoincrement=True)
    blog_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))

    @classmethod
    def exists(cls, db: Session, blog_id: int, user_id: int) -> bool:
        return db.query(cls).filter(cls.blog_id == blog_id, cls.user_id == user_id).first() is not None

    @classmethod
    def create(cls, db: Session, blog_id: int, user_id: int) -> "BlogLike":
        like = cls(blog_id=blog_id, user_id=user_id)
        db.add(like)
        db.commit()
        db.refresh(like)
        return like


# -------------------------------------------------------
# Blog Save (Bookmark)
# -------------------------------------------------------

class BlogSave(Base):
    __tablename__ = "blog_save"

    save_id = Column(Integer().with_variant(
        _mysql_dialect.BIGINT(), "mysql"), primary_key=True, autoincrement=True)
    blog_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))

    @classmethod
    def exists(cls, db: Session, blog_id: int, user_id: int) -> bool:
        return db.query(cls).filter(cls.blog_id == blog_id, cls.user_id == user_id).first() is not None

    @classmethod
    def create(cls, db: Session, blog_id: int, user_id: int) -> "BlogSave":
        save = cls(blog_id=blog_id, user_id=user_id)
        db.add(save)
        db.commit()
        db.refresh(save)
        return save

    @classmethod
    def list_blog_ids_by_user(
        cls,
        db: Session,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        sort: Optional[str] = None,
        order: str = SORT_ORDER_DESC,
    ) -> List[int]:
        query = db.query(cls.blog_id).filter(cls.user_id == user_id)

        normalized_sort = (sort or SORT_BY_CREATE_TIME).lower()
        sort_column_map = {
            SORT_BY_CREATE_TIME.lower(): cls.created_at,
            "createtime": cls.created_at,
            "createdat": cls.created_at,
            "created_at": cls.created_at,
        }
        sort_column = sort_column_map.get(normalized_sort, cls.created_at)

        if order == SORT_ORDER_ASC:
            query = query.order_by(sort_column.asc(), cls.save_id.asc())
        else:
            query = query.order_by(sort_column.desc(), cls.save_id.desc())

        rows = query.offset(offset).limit(limit).all()
        return [row.blog_id for row in rows]


# -------------------------------------------------------
# Blog Report
# -------------------------------------------------------

class BlogReport(Base):
    __tablename__ = "blog_report"

    report_id = Column(Integer().with_variant(
        _mysql_dialect.BIGINT(), "mysql"), primary_key=True, autoincrement=True)
    blog_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    reason = Column(String(512), nullable=True, default="")
    created_at = Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))

    @classmethod
    def exists(cls, db: Session, blog_id: int, user_id: int) -> bool:
        return db.query(cls).filter(cls.blog_id == blog_id, cls.user_id == user_id).first() is not None

    @classmethod
    def create(cls, db: Session, blog_id: int, user_id: int, reason: str = "") -> "BlogReport":
        report = cls(blog_id=blog_id, user_id=user_id, reason=reason or "")
        db.add(report)
        db.commit()
        db.refresh(report)
        return report
