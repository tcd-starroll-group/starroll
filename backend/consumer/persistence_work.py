import json
from kafka import KafkaConsumer
from backend.console.dal.rds.sql.message import Message
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

        new_msg = Message(
            id=data['msg_id'],
            room_id=data['room_id'],
            sender_id=data['sender_id'],
            content=data['content']
        )

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