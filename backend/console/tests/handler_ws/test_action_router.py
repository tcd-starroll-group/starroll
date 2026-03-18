"""Unit tests for backend.console.handler_ws.action_router"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.console.handler_ws import action_router as router_mod
from backend.console.handler_ws.action_router import route_action


def _make_ws() -> AsyncMock:
    ws = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


def _make_manager() -> AsyncMock:
    return AsyncMock()


def _run(manager, ws, payload) -> None:
    asyncio.run(
        route_action(manager=manager, user_id="u1",
                     websocket=ws, payload=payload)
    )


class TestRouteAction:
    def test_missing_action_sends_error(self):
        ws = _make_ws()
        _run(_make_manager(), ws, {})
        sent = ws.send_json.call_args[0][0]
        assert sent["action"] == "Error"
        assert "action is required" in sent["message"]

    def test_empty_action_string_sends_error(self):
        ws = _make_ws()
        _run(_make_manager(), ws, {"action": ""})
        sent = ws.send_json.call_args[0][0]
        assert sent["action"] == "Error"
        assert "action is required" in sent["message"]

    def test_non_string_action_sends_error(self):
        ws = _make_ws()
        _run(_make_manager(), ws, {"action": 123})
        sent = ws.send_json.call_args[0][0]
        assert sent["action"] == "Error"
        assert "action is required" in sent["message"]

    def test_unknown_action_sends_error(self):
        ws = _make_ws()
        _run(_make_manager(), ws, {"action": "UnknownFoo"})
        sent = ws.send_json.call_args[0][0]
        assert sent["action"] == "Error"
        assert "unsupported action" in sent["message"]
        assert "UnknownFoo" in sent["message"]

    def test_heartbeat_action_dispatched(self):
        ws = _make_ws()
        manager = _make_manager()
        mock_handler = AsyncMock()
        with patch.dict(router_mod.ACTION_HANDLERS, {"HeartBeat": mock_handler}):
            _run(manager, ws, {"action": "HeartBeat"})
        mock_handler.assert_awaited_once_with(
            manager=manager, user_id="u1", websocket=ws,
            payload={"action": "HeartBeat"}
        )

    def test_join_chat_room_dispatched(self):
        ws = _make_ws()
        manager = _make_manager()
        mock_handler = AsyncMock()
        payload = {"action": "JoinChatRoom", "ChatRoomID": 1}
        with patch.dict(router_mod.ACTION_HANDLERS, {"JoinChatRoom": mock_handler}):
            _run(manager, ws, payload)
        mock_handler.assert_awaited_once()

    def test_exit_chat_room_dispatched(self):
        ws = _make_ws()
        manager = _make_manager()
        mock_handler = AsyncMock()
        with patch.dict(router_mod.ACTION_HANDLERS, {"ExitChatRoom": mock_handler}):
            _run(manager, ws, {"action": "ExitChatRoom"})
        mock_handler.assert_awaited_once()

    def test_send_message_dispatched(self):
        ws = _make_ws()
        manager = _make_manager()
        mock_handler = AsyncMock()
        payload = {"action": "SendMessage", "message": "hi"}
        with patch.dict(router_mod.ACTION_HANDLERS, {"SendMessage": mock_handler}):
            _run(manager, ws, payload)
        mock_handler.assert_awaited_once()

    def test_all_registered_actions_exist(self):
        assert "HeartBeat" in router_mod.ACTION_HANDLERS
        assert "JoinChatRoom" in router_mod.ACTION_HANDLERS
        assert "ExitChatRoom" in router_mod.ACTION_HANDLERS
        assert "SendMessage" in router_mod.ACTION_HANDLERS
