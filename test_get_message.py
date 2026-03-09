import json
from backend.console.handler.get_message import handle_get_message
from dotenv import load_dotenv
load_dotenv()


def run_test():
    room_id = "star_1001"  # 必须与之前测试发送的 room_id 保持一致

    print("==================================================")
    print(f"🚀 测试 1: 模拟首次进入群聊拉取历史记录 (last_msg_id = 0)")
    print("==================================================")

    # 模拟前端第一次请求，传 0 代表拉取最新的历史记录
    result1 = handle_get_message(room_id, last_msg_id=0)
    print(json.dumps(result1, indent=2, ensure_ascii=False))

    # 如果第一次拉取成功，提取最新的 msg_id 进行第二次测试
    if result1.get("code") == 200 and result1["data"]["messages"]:
        latest_id = int(result1["data"]["latest_msg_id"])

        print("\n==================================================")
        print(f"🚀 测试 2: 模拟断线重连，只拉取增量数据 (last_msg_id = {latest_id})")
        print("==================================================")

        # 模拟前端重连，传入本地记录的最新 msg_id
        result2 = handle_get_message(room_id, last_msg_id=latest_id)
        print(json.dumps(result2, indent=2, ensure_ascii=False))

        if not result2["data"]["messages"]:
            print("\n✅ 测试通过！因为没有新消息，所以增量拉取返回了空列表，完美符合设计！")
    else:
        print("\n⚠️ 数据库中没有找到消息，请先运行 test_chat_flow.py 发送几条测试消息。")


if __name__ == "__main__":
    run_test()