from sqlalchemy import Column, String, BigInteger, Text, DateTime, Index
from datetime import datetime
from .user import Base # 确保引用同一个 Base 以便统一创建

class Message(Base):
    __tablename__ = "chat_messages"

    # 使用 BigInteger 存储 Snowflake ID [cite: 26, 76]
    id = Column(BigInteger, primary_key=True, autoincrement=False, comment='Snowflake ID')
    room_id = Column(String(64), nullable=False, index=True, comment='星星HIP/群聊ID')
    sender_id = Column(BigInteger, nullable=False, comment='发送者ID')
    content = Column(Text, nullable=False, comment='消息内容或MinIO URL') [cite: 23, 74]
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 联合索引优化 getMessage 接口的差量查询 [cite: 40, 92]
    __table_args__ = (
        Index('idx_room_msg', 'room_id', 'id'),
    )