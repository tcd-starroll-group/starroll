from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.console.websocket.action_router import route_action
from backend.console.websocket.connection_manager import ConnectionManager

router = APIRouter()
connection_manager = ConnectionManager()


@router.websocket("/api/chat")
async def api_chat(websocket: WebSocket) -> None:
    await websocket.accept()
    user_id = websocket.query_params.get("user_id")
    await connection_manager.connect(user_id, websocket)

    try:
        while True:
            try:
                payload = await websocket.receive_json()
            except ValueError:
                await websocket.send_json({"action": "Error", "message": "invalid json payload"})
                continue

            if not isinstance(payload, dict):
                await websocket.send_json({"action": "Error", "message": "payload must be a json object"})
                continue

            await route_action(
                manager=connection_manager,
                user_id=user_id,
                websocket=websocket,
                payload=payload,
            )
    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.disconnect(user_id)
