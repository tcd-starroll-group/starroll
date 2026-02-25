import asyncio
import json

# 导入你刚刚写好的消息处理函数
from backend.console.handler.chat import handle_send_message


# 模拟一个 WebSocket 连接对象
class MockWebSocket:
    async def send(self, data):
        # 当后端调用 await websocket.send() 时，会触发这里
        print(f"\n✅ [客户端收到响应 ACK]: {data}")


async def run_test():
    # 1. 模拟用户和消息载体
    ws = MockWebSocket()
    mock_user_id = 999
    mock_payload = {
        "room_id": "star_1001",
        "content": "Hello Universe! 这是一条来自本地测试的消息。"
    }

    print("🚀 开始模拟发送群聊消息...")
    print(f"发送内容: {json.dumps(mock_payload, ensure_ascii=False)}")

    # 2. 调用 Console 的处理逻辑
    await handle_send_message(ws, mock_user_id, mock_payload)

    print("✨ Console 处理逻辑执行完毕！")


if __name__ == "__main__":
    # 运行异步测试
    asyncio.run(run_test())