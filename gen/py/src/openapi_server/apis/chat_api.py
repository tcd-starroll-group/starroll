from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.console.utils.auth import verify_access_token
from backend.console.handler_ws.action_router import route_action
from backend.console.handler_ws.connection_manager import ConnectionManager

router = APIRouter()
connection_manager = ConnectionManager()


@router.websocket("/api/chat")
async def api_chat(websocket: WebSocket) -> None:
    auth_header = websocket.headers.get("Authorization")
    if not auth_header:
        await websocket.close(code=1008, reason="Authorization header required")
        return

    if auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):].strip()
    else:
        token = auth_header.strip()

    if not token:
        await websocket.close(code=1008, reason="Invalid Authorization header")
        return

    token_payload, is_valid = verify_access_token(token)
    if not is_valid or token_payload is None:
        await websocket.close(code=1008, reason="Invalid or expired token")
        return
    user_id = token_payload.get("user_id")

    await websocket.accept()
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
