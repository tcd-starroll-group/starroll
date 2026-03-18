from __future__ import annotations

import json

from fastapi import WebSocket

from backend.console.dal import get_kafka_client, get_redis_client
from backend.console.utils.snow_flake import gen_snowflake_id
from backend.console.handler_ws.connection_manager import ConnectionManager
from backend.constant.kafka import TOPIC_CHAT_MESSAGE
from backend.model.chat import ChatMessageKafkaEvent, ErrorAction, SendMessageAction


async def handle(*, manager: ConnectionManager, user_id: str, websocket: WebSocket, payload: dict) -> None:
    try:
        request = SendMessageAction(**payload)
    except Exception:
        await websocket.send_json(
            ErrorAction(action="Error",
                        message="invalid SendMessage payload").model_dump()
        )
        return

    message = request.message
    if not message.strip():
        print(
            "SendMessage rejected: empty message user_id=%s", user_id)
        await websocket.send_json(
            ErrorAction(action="Error",
                        message="message is required").model_dump()
        )
        return

    room_id = await manager.get_user_room(user_id)
    if room_id is None:
        print(
            "SendMessage rejected: user not in room user_id=%s", user_id)
        await websocket.send_json(
            ErrorAction(action="Error",
                        message="not in any chat room").model_dump()
        )
        return

    message_id = gen_snowflake_id()

    event = ChatMessageKafkaEvent(
        user_id=user_id,
        chatroom_id=room_id,
        message_id=message_id,
        message=message.strip(),
    )

    try:
        producer = get_kafka_client().get_producer()

        def _on_delivery(err, msg):
            if err:
                print(
                    "Kafka delivery error topic=%s room_id=%s message_id=%s err=%s",
                    TOPIC_CHAT_MESSAGE, room_id, message_id, err,
                )

        producer.produce(
            topic=TOPIC_CHAT_MESSAGE,
            key=str(room_id).encode(),
            value=event.model_dump_json().encode(),
            on_delivery=_on_delivery,
        )
        # poll(0) triggers delivery callbacks without blocking the event loop.
        producer.poll(0)
        print("Published chat message to kafka topic=%s room_id=%s message_id=%s",
              TOPIC_CHAT_MESSAGE, room_id, message_id)

        redis_channel = f"chat:room:{room_id}"
        delivered = get_redis_client().publish(redis_channel, event.model_dump_json())
        print(
            "Published chat message to redis channel=%s receivers=%s room_id=%s message_id=%s",
            redis_channel,
            delivered,
            room_id,
            message_id,
        )
    except Exception as exc:
        print("Failed to publish chat message to Kafka/Redis: %s", exc)
        await websocket.send_json(
            ErrorAction(action="Error",
                        message="failed to send message").model_dump()
        )
