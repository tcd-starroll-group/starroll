import uuid
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Column, String, Text, text
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class StarMessage(Base):
    """star_messages table model definition"""

    __tablename__ = "star_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    message_id = Column(String(64), nullable=False, unique=True)
    hip = Column(String(32), nullable=False)
    from_ = Column("from", String(32), nullable=False)
    message = Column(Text, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False,
                        server_default=text("0"))

    @classmethod
    def create(
        cls,
        db: Session,
        user_id: int,
        hip: str,
        from_: str,
        message: str,
    ) -> "StarMessage":
        item = cls(
            user_id=user_id,
            message_id=str(uuid.uuid4()),
            hip=hip,
            from_=from_,
            message=message,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @classmethod
    def get_by_message_id(cls, db: Session, message_id: str) -> Optional["StarMessage"]:
        return db.query(cls).filter(
            cls.message_id == message_id,
            cls.is_deleted == False,  # noqa: E712
        ).first()
