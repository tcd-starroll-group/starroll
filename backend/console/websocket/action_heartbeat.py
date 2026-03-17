from __future__ import annotations

from fastapi import WebSocket

from backend.console.websocket.connection_manager import ConnectionManager


async def handle(*, manager: ConnectionManager, user_id: str, websocket: WebSocket, payload: dict) -> None:
    _ = websocket
    _ = payload
    await manager.update_heartbeat(user_id)
