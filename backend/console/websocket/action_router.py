from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import WebSocket

from backend.model.chat import ErrorAction
from backend.console.websocket import (
    action_exit_chat_room,
    action_heartbeat,
    action_join_chat_room,
    action_send_message,
)
from backend.console.websocket.connection_manager import ConnectionManager

ActionHandler = Callable[..., Awaitable[None]]

ACTION_HANDLERS: dict[str, ActionHandler] = {
    "HeartBeat": action_heartbeat.handle,
    "JoinChatRoom": action_join_chat_room.handle,
    "ExitChatRoom": action_exit_chat_room.handle,
    "SendMessage": action_send_message.handle,
}


async def route_action(*, manager: ConnectionManager, user_id: str, websocket: WebSocket, payload: dict[str, Any]) -> None:
    action = payload.get("action")
    if not isinstance(action, str) or not action:
        await websocket.send_json(
            ErrorAction(action="Error", message="action is required").dict()
        )
        return

    handler = ACTION_HANDLERS.get(action)
    if handler is None:
        await websocket.send_json(
            ErrorAction(action="Error",
                        message=f"unsupported action: {action}").dict()
        )
        return

    await handler(manager=manager, user_id=user_id, websocket=websocket, payload=payload)
