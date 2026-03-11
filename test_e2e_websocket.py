import asyncio
import json
import websockets  # if error, run: pip install websockets


async def test_websocket_e2e():
    uri = "ws://localhost:8000/api/chat/ws/999"

    print(f"🔄 正在尝试连接 WebSocket 服务: {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 连接成功！")

            payload = {
                "room_id": "star_1001",
                "content": "这是一条真实的 End-to-End WebSocket 测试消息！"
            }

            print(f"🚀 正在发送: {json.dumps(payload, ensure_ascii=False)}")
            await websocket.send(json.dumps(payload))

            response = await websocket.recv()
            print(f"✨ 收到服务器 ACK 响应: {response}")

    except Exception as e:
        print(f"❌ 连接或通讯失败: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket_e2e())