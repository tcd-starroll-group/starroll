"""Consumer for chat messages: reads from Kafka and persists to MySQL."""

from __future__ import annotations

import json
import time
import signal
import sys
from types import FrameType
from typing import Optional

from backend.config import settings
from backend.console.dal import get_kafka_client
from backend.console.dal.rds.chat_messages import ChatMessages
from backend.console.dal.rds.client import SessionLocal
from backend.constant.kafka import TOPIC_CHAT_MESSAGE


_running = True


def _on_assign(consumer, partitions) -> None:
    print(f"Consumer assigned partitions: {partitions}")
    consumer.assign(partitions)


def _on_revoke(consumer, partitions) -> None:
    print(f"Consumer revoked partitions: {partitions}")


def _handle_shutdown(sig: int, frame: Optional[FrameType]) -> None:
    global _running
    print("Shutdown signal received, stopping consumer...")
    _running = False


def _wait_for_topic(consumer, topic: str) -> None:
    """Wait for topic to become available, retrying every 5 seconds."""
    retry_count = 0
    while True:
        try:
            metadata = consumer.list_topics(topic, timeout=5)
            topic_meta = metadata.topics.get(topic)
            if topic_meta is None:
                retry_count += 1
                print(
                    f"Topic metadata missing: {topic}, retrying in 5s... (attempt {retry_count})")
                time.sleep(5)
                continue
            else:
                print(
                    f"Topic metadata loaded topic={topic} "
                    f"partitions={list(topic_meta.partitions.keys())} "
                    f"error={topic_meta.error}"
                )
                return
        except Exception as exc:
            retry_count += 1
            print(
                f"Failed to fetch topic metadata: {exc}, retrying in 5s... (attempt {retry_count})")
            time.sleep(5)


def _process_message(event: dict) -> None:
    user_id: Optional[int] = event.get("user_id")
    chatroom_id: Optional[int] = event.get("chatroom_id")
    message_id: Optional[int] = event.get("message_id")
    message: Optional[str] = event.get("message")

    if any(v is None for v in [user_id, chatroom_id, message_id, message]):
        print("Dropping malformed chat message event: %s", event)
        return

    if SessionLocal is None:
        print("Database not configured; cannot persist chat message")
        return

    with SessionLocal() as db:
        ChatMessages.create(
            db=db,
            user_id=int(user_id),
            chatroom_id=int(chatroom_id),
            message_id=int(message_id),
            message=str(message),
        )
    print("Persisted chat message %s for chatroom %s",
          message_id, chatroom_id)


def run() -> None:
    signal.signal(signal.SIGINT, _handle_shutdown)
    signal.signal(signal.SIGTERM, _handle_shutdown)

    consumer = get_kafka_client(settings).get_consumer("chat_message_to_rds")

    # Wait for topic to be available before subscribing
    _wait_for_topic(consumer, TOPIC_CHAT_MESSAGE)

    consumer.subscribe([TOPIC_CHAT_MESSAGE],
                       on_assign=_on_assign, on_revoke=_on_revoke)

    print(
        "ChatMessage consumer started "
        f"bootstrap={settings.kafka_bootstrap_servers} "
        f"offset_reset={settings.kafka_auto_offset_reset} "
        f"topic={TOPIC_CHAT_MESSAGE}"
    )

    last_idle_log_time = time.time()

    try:
        while _running:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                now = time.time()
                if now - last_idle_log_time >= 30:
                    assigned = consumer.assignment()
                    print("Consumer idle for 30s ")
                    last_idle_log_time = now
                continue
            if msg.error():
                print(f"Kafka error: {msg.error()}")
                continue

            try:
                event = json.loads(msg.value().decode())
                _process_message(event)
                print(
                    "Chat message persisted "
                    f"message_id={event.get('message_id')} chatroom_id={event.get('chatroom_id')}"
                )
            except Exception as exc:
                print(
                    f"Failed to process chat message: {exc}, raw={msg.value()}")
    finally:
        consumer.close()
        print("ChatMessage consumer stopped")


if __name__ == "__main__":
    run()
    sys.exit(0)
