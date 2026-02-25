import json
from kafka import KafkaConsumer
# 修复点：修正导入路径
from backend.console.dal.rds.sql.message import Message
# 修复点：从 client.py 导入的是 SessionLocal，而不是 Session
from backend.console.dal.rds.client import SessionLocal

consumer = KafkaConsumer(
    'chat_messages',
    bootstrap_servers='localhost:9092',
    group_id='persistence_group',
    auto_offset_reset='earliest'
)


def start_consuming():
    print("Persistence worker started...")
    for message in consumer:
        data = json.loads(message.value)

        # 5. 由专用 Consumer 批量异步写入 MySQL [cite: 27, 78]
        new_msg = Message(
            id=data['msg_id'],
            room_id=data['room_id'],
            sender_id=data['sender_id'],
            content=data['content']
        )

        # 修复点：使用 SessionLocal() 创建会话实例
        session = SessionLocal()
        try:
            session.add(new_msg)
            session.commit()
        except Exception as e:
            print(f"Error persisting message: {e}")
            session.rollback()
        finally:
            session.close()


if __name__ == "__main__":
    start_consuming()