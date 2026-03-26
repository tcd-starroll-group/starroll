from __future__ import annotations

from fastapi import WebSocket

from backend.console.dal.rds.chat_messages import ChatMessages
from backend.console.dal.rds.client import SessionLocal
from backend.console.handler_ws.chat_message_formatter import build_chat_messages_action
from backend.console.handler_ws.connection_manager import ConnectionManager
from backend.model.chat import ErrorAction, ListMessagesAction


async def handle(*, manager: ConnectionManager, user_id: str, websocket: WebSocket, payload: dict) -> None:
    del manager, user_id

    try:
        request = ListMessagesAction(**payload)
    except Exception:
        await websocket.send_json(
            ErrorAction(action="Error",
                        message="invalid ListMessages payload").model_dump()
        )
        return

    if SessionLocal is None:
        await websocket.send_json(
            ErrorAction(action="Error",
                        message="database is not configured").model_dump()
        )
        return

    with SessionLocal() as db:
        messages = ChatMessages.list_by_chatroom(
            db=db,
            chatroom_id=request.ChatRoomID,
            since_message_id=request.SinceMessageID,
            before_message_id=request.Before,
            limit=1000,
        )
        response = build_chat_messages_action(db, list(messages))

    await websocket.send_json(response.model_dump())
