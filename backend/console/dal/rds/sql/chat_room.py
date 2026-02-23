from sqlalchemy import Column, String, DateTime
from datetime import datetime
from .user import Base

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    # room_id 对应星星的 HIP [cite: 29, 80]
    id = Column(String(64), primary_key=True, comment='星星HIP')
    name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)