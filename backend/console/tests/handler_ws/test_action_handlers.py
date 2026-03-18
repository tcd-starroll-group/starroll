"""Unit tests for action_heartbeat, action_exit_chat_room, action_join_chat_room, action_send_message."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.console.handler_ws import (
    action_exit_chat_room,
    action_heartbeat,
    action_join_chat_room,
    action_send_message,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ws() -> AsyncMock:
    ws = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


def _make_manager() -> AsyncMock:
    m = AsyncMock()
    return m


# ===========================================================================
# action_heartbeat
# ===========================================================================

class TestActionHeartbeat:
    def test_calls_update_heartbeat(self):
        manager = _make_manager()
        ws = _make_ws()
        asyncio.run(
            action_heartbeat.handle(
                manager=manager, user_id="u1", websocket=ws, payload={}
            )
        )
        manager.update_heartbeat.assert_awaited_once_with("u1")

    def test_no_response_sent_to_ws(self):
        manager = _make_manager()
        ws = _make_ws()
        asyncio.run(
            action_heartbeat.handle(
                manager=manager, user_id="u1", websocket=ws, payload={}
            )
        )
        ws.send_json.assert_not_called()


# ===========================================================================
# action_exit_chat_room
# ===========================================================================

class TestActionExitChatRoom:
    def test_calls_exit_room(self):
        manager = _make_manager()
        ws = _make_ws()
        asyncio.run(
            action_exit_chat_room.handle(
                manager=manager, user_id="u2", websocket=ws, payload={}
            )
        )
        manager.exit_room.assert_awaited_once_with("u2")

    def test_no_response_sent_to_ws(self):
        manager = _make_manager()
        ws = _make_ws()
        asyncio.run(
            action_exit_chat_room.handle(
                manager=manager, user_id="u2", websocket=ws, payload={}
            )
        )
        ws.send_json.assert_not_called()


# ===========================================================================
# action_join_chat_room
# ===========================================================================

class TestActionJoinChatRoom:
    def _run(self, manager, ws, payload):
        asyncio.run(
            action_join_chat_room.handle(
                manager=manager, user_id="u3", websocket=ws, payload=payload
            )
        )

    def test_invalid_payload_sends_error(self):
        manager = _make_manager()
        ws = _make_ws()
        self._run(manager, ws, {"action": "JoinChatRoom", "ChatRoomID": "bad"})
        sent = ws.send_json.call_args[0][0]
        assert sent["action"] == "Error"

    def test_valid_payload_joins_room(self, db_session):
        import backend.console.handler_ws.action_join_chat_room as mod

        manager = _make_manager()
        ws = _make_ws()

        fake_session_factory = MagicMock(return_value=MagicMock(
            __enter__=lambda s, *a: db_session,
            __exit__=lambda s, *a: None,
        ))

        with patch.object(mod, "SessionLocal", fake_session_factory), \
                patch.object(mod, "ChatMessages") as mock_cm, \
                patch.object(mod, "build_chat_messages_action") as mock_fmt:
            mock_cm.list_by_chatroom.return_value = []
            from backend.model.chat import ChatMessagesAction
            mock_fmt.return_value = ChatMessagesAction(
                action="ChatMessages", messages=[])
            self._run(
                manager, ws,
                {"action": "JoinChatRoom", "ChatRoomID": 42, "SinceMessageID": None}
            )

        manager.join_room.assert_awaited_once_with("u3", "42")
        ws.send_json.assert_called_once()
        assert ws.send_json.call_args[0][0]["action"] == "ChatMessages"

    def test_valid_payload_with_since_message_id(self, db_session):
        import backend.console.handler_ws.action_join_chat_room as mod

        manager = _make_manager()
        ws = _make_ws()

        fake_session_factory = MagicMock(return_value=MagicMock(
            __enter__=lambda s, *a: db_session,
            __exit__=lambda s, *a: None,
        ))

        with patch.object(mod, "SessionLocal", fake_session_factory), \
                patch.object(mod, "ChatMessages") as mock_cm, \
                patch.object(mod, "build_chat_messages_action") as mock_fmt:
            mock_cm.list_by_chatroom.return_value = []
            from backend.model.chat import ChatMessagesAction
            mock_fmt.return_value = ChatMessagesAction(
                action="ChatMessages", messages=[])
            self._run(
                manager, ws,
                {"action": "JoinChatRoom", "ChatRoomID": 42, "SinceMessageID": 100}
            )

        mock_cm.list_by_chatroom.assert_called_once()
        call_kwargs = mock_cm.list_by_chatroom.call_args[1]
        assert call_kwargs["since_message_id"] == 100

    def test_session_local_none_sends_error(self):
        import backend.console.handler_ws.action_join_chat_room as mod
        manager = _make_manager()
        ws = _make_ws()
        with patch.object(mod, "SessionLocal", None):
            self._run(
                manager, ws,
                {"action": "JoinChatRoom", "ChatRoomID": 5}
            )
        sent = ws.send_json.call_args[0][0]
        assert sent["action"] == "Error"
        assert "database" in sent["message"].lower()


# ===========================================================================
# action_send_message
# ===========================================================================

class TestActionSendMessage:
    def _run(self, manager, ws, payload):
        asyncio.run(
            action_send_message.handle(
                manager=manager, user_id="u4", websocket=ws, payload=payload
            )
        )

    def test_invalid_payload_sends_error(self):
        manager = _make_manager()
        ws = _make_ws()
        # missing 'message' field
        self._run(manager, ws, {"action": "SendMessage"})
        sent = ws.send_json.call_args[0][0]
        assert sent["action"] == "Error"

    def test_empty_message_sends_error(self):
        manager = _make_manager()
        ws = _make_ws()
        manager.get_user_room = AsyncMock(return_value="room1")
        self._run(manager, ws, {"action": "SendMessage", "message": "   "})
        sent = ws.send_json.call_args[0][0]
        assert sent["action"] == "Error"
        assert "message is required" in sent["message"]

    def test_user_not_in_room_sends_error(self):
        manager = _make_manager()
        ws = _make_ws()
        manager.get_user_room = AsyncMock(return_value=None)
        self._run(manager, ws, {"action": "SendMessage", "message": "hello"})
        sent = ws.send_json.call_args[0][0]
        assert sent["action"] == "Error"
        assert "chat room" in sent["message"]

    def test_success_publishes_to_kafka_and_redis(self):
        import backend.console.handler_ws.action_send_message as mod

        manager = _make_manager()
        manager.get_user_room = AsyncMock(return_value="room99")
        ws = _make_ws()

        mock_producer = MagicMock()
        mock_kafka = MagicMock()
        mock_kafka.get_producer.return_value = mock_producer

        mock_redis = MagicMock()
        mock_redis.publish.return_value = 1

        with patch.object(mod, "get_kafka_client", return_value=mock_kafka), \
                patch.object(mod, "get_redis_client", return_value=mock_redis), \
                patch.object(mod, "gen_snowflake_id", return_value=12345):
            self._run(manager, ws, {
                      "action": "SendMessage", "message": "hello world"})

        mock_producer.produce.assert_called_once()
        mock_producer.poll.assert_called_once_with(0)
        mock_redis.publish.assert_called_once()
        ws.send_json.assert_not_called()

    def test_kafka_redis_exception_sends_error(self):
        import backend.console.handler_ws.action_send_message as mod

        manager = _make_manager()
        manager.get_user_room = AsyncMock(return_value="room99")
        ws = _make_ws()

        with patch.object(mod, "get_kafka_client", side_effect=Exception("kafka down")), \
                patch.object(mod, "get_redis_client", return_value=MagicMock()), \
                patch.object(mod, "gen_snowflake_id", return_value=99):
            self._run(manager, ws, {
                      "action": "SendMessage", "message": "fail test"})

        sent = ws.send_json.call_args[0][0]
        assert sent["action"] == "Error"
        assert "failed to send" in sent["message"]
