from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.console.dal.rds.chat_messages import ChatMessages
from backend.console.dal.rds.user import User
from backend.model.chat import ChatMessageItem, ChatMessageKafkaEvent, ChatMessagesAction


def build_chat_message_items(db: Session, messages: list[ChatMessages]) -> list[ChatMessageItem]:
    user_ids = {int(item.user_id) for item in messages}
    usernames: dict[int, str] = {}
    for uid in user_ids:
        user = User.get_by_id(db, uid)
        usernames[uid] = user.username if user else str(uid)

    response_messages: list[ChatMessageItem] = []
    for item in messages:
        created_at = item.created_at
        if isinstance(created_at, datetime):
            timestamp = int(created_at.timestamp())
        else:
            timestamp = 0

        response_messages.append(
            ChatMessageItem(
                username=usernames.get(int(item.user_id), str(item.user_id)),
                timestamp=timestamp,
                message=item.message,
                message_id=int(item.message_id),
            )
        )

    return response_messages


def build_chat_messages_action(db: Session, messages: list[ChatMessages]) -> ChatMessagesAction:
    return ChatMessagesAction(
        action="ChatMessages",
        messages=build_chat_message_items(db, messages),
    )


def build_chat_messages_action_from_event(db: Session, event: ChatMessageKafkaEvent) -> ChatMessagesAction:
    user = User.get_by_id(db, int(event.user_id))
    username = user.username if user else str(event.user_id)

    return ChatMessagesAction(
        action="ChatMessages",
        messages=[
            ChatMessageItem(
                username=username,
                timestamp=int(datetime.now(timezone.utc).timestamp()),
                message=event.message,
                message_id=int(event.message_id),
            )
        ],
    )
