import json
import time
from kafka import KafkaProducer
from redis import StrictRedis
from backend.console.utils.snowflake import id_worker
from fastapi import WebSocket, WebSocketDisconnect

# 初始化连接 (建议从 config 获取配置)
kafka_prod = KafkaProducer(bootstrap_servers=['localhost:9092'],
                           api_version=(3, 0, 0),
                           value_serializer=lambda v: json.dumps(v).encode('utf-8')
                           )
redis_client = StrictRedis(host='localhost', port=6379, db=0)


async def handle_send_message(websocket, user_id, payload):
    room_id = payload.get('room_id')

    msg_id = id_worker.get_id()

    full_msg = {
        "msg_id": msg_id,
        "sender_id": user_id,
        "room_id": room_id,
        "content": payload.get('content'),
        "created_at": int(time.time())
    }

    kafka_prod.send('chat_messages', full_msg)

    redis_client.publish(f"group:channel:{room_id}", json.dumps(full_msg))

    await websocket.send_text(json.dumps({
        "status": "ACK",
        "msg_id": str(msg_id)  # 建议转 String 避免 JS 精度丢失
    }))

async def chat_websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    print(f"[WebSocket] User {user_id} connected.")
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            await handle_send_message(websocket, user_id, payload)

    except WebSocketDisconnect:
        print(f"[WebSocket] User {user_id} disconnected normally.")
    except Exception as e:
        print(f"[WebSocket] Error occurred for User {user_id}: {e}")
        await websocket.close()