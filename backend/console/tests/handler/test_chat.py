import pytest
import json
from unittest.mock import AsyncMock, patch
from backend.console.handler.chat import handle_send_message

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.asyncio
# 拦截（Mock）掉外部依赖，防止测试时真的去连本地端口
@patch('backend.console.handler.chat.kafka_prod')
@patch('backend.console.handler.chat.redis_client')
@patch('backend.console.handler.chat.id_worker')
async def test_handle_send_message(mock_id_worker, mock_redis, mock_kafka):
    # 1. 设置 Mock 的返回值
    mock_id_worker.get_id.return_value = 888899990000  # 伪造一个 Snowflake ID

    mock_ws = AsyncMock()
    user_id = 999
    payload = {
        "room_id": "star_1001",
        "content": "Test Message"
    }

    # 2. 执行目标函数
    await handle_send_message(mock_ws, user_id, payload)

    # 3. 断言验证逻辑是否按预期执行
    # 验证 Kafka 被调用了 send，且 topic 是 chat_messages
    mock_kafka.send.assert_called_once()
    kafka_args = mock_kafka.send.call_args[0]
    assert kafka_args[0] == 'chat_messages'
    assert kafka_args[1]['msg_id'] == 888899990000

    # 验证 Redis 被调用了 publish
    mock_redis.publish.assert_called_once()
    redis_args = mock_redis.publish.call_args[0]
    assert redis_args[0] == "group:channel:star_1001"

    # 验证 WebSocket 给前端返回了 ACK，且 msg_id 变成了字符串
    mock_ws.send.assert_called_once()
    ws_sent_data = json.loads(mock_ws.send.call_args[0][0])
    assert ws_sent_data["status"] == "ACK"
    assert ws_sent_data["msg_id"] == "888899990000"