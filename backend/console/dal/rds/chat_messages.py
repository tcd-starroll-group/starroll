from typing import List, Optional

from sqlalchemy import BigInteger, Column, Text, TIMESTAMP, text
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class ChatMessages(Base):
    """chat_messages table model definition"""

    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    chatroom_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))

    @classmethod
    def create(cls, db: Session, user_id: int, chatroom_id: int, message_id: int, message: str) -> "ChatMessages":
        item = cls(
            user_id=user_id,
            chatroom_id=chatroom_id,
            message_id=message_id,
            message=message,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @classmethod
    def get_by_message_id(cls, db: Session, chatroom_id: int, message_id: int) -> Optional["ChatMessages"]:
        return db.query(cls).filter(
            cls.chatroom_id == chatroom_id,
            cls.message_id == message_id,
        ).first()

    @classmethod
    def list_by_chatroom(
            cls,
            db: Session,
            chatroom_id: int,
            since_message_id: Optional[int] = None,
            before_message_id: Optional[int] = None,
            limit: int = 1000,
    ) -> List["ChatMessages"]:
        safe_limit = max(1, min(limit, 1000))
        query = db.query(cls).filter(cls.chatroom_id == chatroom_id)

        if since_message_id is not None:
            query = query.filter(cls.message_id > since_message_id)

        if before_message_id is not None:
            query = query.filter(cls.message_id < before_message_id)

        return query.order_by(cls.message_id.desc()).limit(safe_limit).all()
