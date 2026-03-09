from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.sql.message import Message


def handle_get_message(room_id: str, last_msg_id: int):
    """
    处理获取历史消息的 API 请求
    """
    # 获取数据库 session (使用 next() 是因为 get_db 是个生成器)
    db = next(get_db())

    try:
        # 调用 DAL 层拉取数据
        messages = Message.get_delta_messages(db, room_id, last_msg_id)

        # 格式化返回给前端的数据
        result = []
        for msg in messages:
            result.append({
                "msg_id": str(msg.id),  # 必须转为 String，防止前端 JS 丢失 64 位整数精度
                "sender_id": msg.sender_id,
                "content": msg.content,
                "created_at": msg.created_at.timestamp()
            })

        return {
            "code": 200,
            "message": "success",
            "data": {
                "room_id": room_id,
                "messages": result,
                # 告诉前端当前拉取到的最新 ID 是什么，方便它下次传
                "latest_msg_id": result[-1]["msg_id"] if result else str(last_msg_id)
            }
        }
    except Exception as e:
        return {"code": 500, "message": f"Server Error: {str(e)}"}
    finally:
        db.close()