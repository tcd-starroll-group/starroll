from __future__ import annotations

from fastapi import WebSocket

from backend.console.dal.rds.chat_messages import ChatMessages
from backend.console.dal.rds.client import SessionLocal
from backend.console.handler_ws.chat_message_formatter import build_chat_messages_action
from backend.console.handler_ws.connection_manager import ConnectionManager
from backend.model.chat import ErrorAction, JoinChatRoomAction


async def handle(*, manager: ConnectionManager, user_id: str, websocket: WebSocket, payload: dict) -> None:
    try:
        request = JoinChatRoomAction(**payload)
    except Exception:
        await websocket.send_json(
            ErrorAction(action="Error",
                        message="invalid JoinChatRoom payload").model_dump()
        )
        return

    room_id = str(request.ChatRoomID)
    room_id_int = request.ChatRoomID

    await manager.join_room(user_id, room_id)

    since_message_id = request.SinceMessageID

    if SessionLocal is None:
        await websocket.send_json(
            ErrorAction(action="Error",
                        message="database is not configured").model_dump()
        )
        return

    with SessionLocal() as db:
        messages = ChatMessages.list_by_chatroom(
            db=db,
            chatroom_id=room_id_int,
            since_message_id=since_message_id,
            limit=1000,
        )

        messages = list(messages)
        response = build_chat_messages_action(db, messages)

    await websocket.send_json(
        response.model_dump()
    )
