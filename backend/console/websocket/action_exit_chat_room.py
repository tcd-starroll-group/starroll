from __future__ import annotations

from fastapi import WebSocket

from backend.console.websocket.connection_manager import ConnectionManager


async def handle(*, manager: ConnectionManager, user_id: str, websocket: WebSocket, payload: dict) -> None:
    await manager.exit_room(user_id)
