import json
import time
from kafka import KafkaProducer
from redis import StrictRedis
from backend.console.utils.snowflake import id_worker

# 初始化连接 (建议从 config 获取配置)
kafka_prod = KafkaProducer(bootstrap_servers='localhost:9092')
redis_client = StrictRedis(host='localhost', port=6379, db=0)


async def handle_send_message(websocket, user_id, payload):
    """
    payload 格式参考文档: { "room_id": "star_1001", "content": "hello", "type": 0 }
    """
    room_id = payload.get('room_id')

    # 1. 后端进行权限检查 (是否为好友、是否被拉黑) [cite: 21, 72]
    # if not check_user_permission(user_id, room_id):
    #     return await websocket.send(json.dumps({"error": "No permission"}))

    # 2. 生成唯一的 msg_id
    msg_id = id_worker.get_id()

    full_msg = {
        "msg_id": msg_id,
        "sender_id": user_id,
        "room_id": room_id,
        "content": payload.get('content'),
        "created_at": int(time.time())
    }

    # 3. 异步并行处理：
    # A. 发送到 Kafka 的 chat_messages Topic [cite: 24, 75]
    kafka_prod.send('chat_messages', json.dumps(full_msg).encode('utf-8'))

    # B. 发布到 Redis 对应的 channel (以星星 HIP 为名)
    redis_client.publish(f"group:channel:{room_id}", json.dumps(full_msg))

    # 4. 向发送者返回 ACK，确认服务器已收到 [cite: 26, 77]
    await websocket.send(json.dumps({
        "status": "ACK",
        "msg_id": str(msg_id)  # 建议转 String 避免 JS 精度丢失
    }))