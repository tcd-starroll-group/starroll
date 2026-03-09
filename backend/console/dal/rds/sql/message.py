from sqlalchemy import Column, String, BigInteger, Text, DateTime, Index
from datetime import datetime
from backend.console.dal.rds.user import Base
from sqlalchemy.orm import Session
from typing import List

class Message(Base):
    __tablename__ = "chat_messages"

    # 使用 BigInteger 存储 Snowflake ID
    id = Column(BigInteger, primary_key=True, autoincrement=False, comment='Snowflake ID')
    room_id = Column(String(64), nullable=False, index=True, comment='星星HIP/群聊ID')
    sender_id = Column(BigInteger, nullable=False, comment='发送者ID')
    content = Column(Text, nullable=False, comment='消息内容或MinIO URL')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 联合索引优化 getMessage 接口的差量查询
    __table_args__ = (
        Index('idx_room_msg', 'room_id', 'id'),
    )


    @classmethod
    def get_delta_messages(cls, db: Session, room_id: str, last_msg_id: int, limit: int = 100) -> List["Message"]:
        """
        拉取差量历史消息
        :param db: 数据库 Session
        :param room_id: 群聊星系 HIP
        :param last_msg_id: 客户端传来的最新消息 ID (如果是首次进入，传 0)
        :param limit: 每次最多拉取条数，保护数据库
        :return: 消息列表，按时间正序排列
        """
        return db.query(cls)\
            .filter(cls.room_id == room_id, cls.id > last_msg_id)\
            .order_by(cls.id.asc())\
            .limit(limit)\
            .all()