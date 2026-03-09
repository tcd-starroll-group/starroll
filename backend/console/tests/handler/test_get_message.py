import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from backend.console.handler.get_message import handle_get_message


# 伪造一个数据库查询返回的对象
class MockMessageObj:
    def __init__(self, id, sender_id, content):
        self.id = id
        self.sender_id = sender_id
        self.content = content
        self.created_at = datetime.now()


@patch('backend.console.handler.get_message.get_db')
@patch('backend.console.handler.get_message.Message.get_delta_messages')
def test_handle_get_message_success(mock_get_delta, mock_get_db):
    # 1. 伪造 get_db 返回一个 mock session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])

    # 2. 伪造数据库查出了两条历史消息
    mock_get_delta.return_value = [
        MockMessageObj(id=1001, sender_id=999, content="Msg 1"),
        MockMessageObj(id=1002, sender_id=888, content="Msg 2")
    ]

    # 3. 执行函数
    response = handle_get_message("star_1001", last_msg_id=1000)

    # 4. 验证返回值格式和数据处理逻辑
    assert response["code"] == 200
    assert len(response["data"]["messages"]) == 2
    assert response["data"]["latest_msg_id"] == "1002"
    assert response["data"]["messages"][0]["content"] == "Msg 1"

    # 验证查库逻辑是否把正确的参数传进去了
    mock_get_delta.assert_called_once_with(mock_session, "star_1001", 1000)

    # 验证 session.close() 被调用，防止数据库连接泄露
    mock_session.close.assert_called_once()