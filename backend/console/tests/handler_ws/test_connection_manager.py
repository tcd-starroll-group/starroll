"""Unit tests for ConnectionManager."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from backend.console.handler_ws.connection_manager import ConnectionManager


class TestConnectionManager:
    """Tests for ConnectionManager."""

    @pytest.fixture
    def manager(self):
        """Create a ConnectionManager instance with mocked SessionLocal."""
        with patch("backend.console.handler_ws.connection_manager.SessionLocal") as mock_session:
            mock_session.__enter__ = Mock(return_value=MagicMock())
            mock_session.__exit__ = Mock(return_value=None)
            with patch.object(
                ConnectionManager, "_ensure_heartbeat_checker_started"
            ) as mock_hb_start, patch.object(
                ConnectionManager, "_ensure_pubsub_listener_started"
            ) as mock_pubsub_start:
                manager = ConnectionManager()
                # Patch the methods to prevent real task creation
                manager._ensure_heartbeat_checker_started = mock_hb_start
                manager._ensure_pubsub_listener_started = mock_pubsub_start
                yield manager

    def _make_websocket(self) -> AsyncMock:
        """Create a mocked WebSocket."""
        ws = AsyncMock()
        ws.send_json = AsyncMock()
        ws.close = AsyncMock()
        return ws

    # =====================================================================
    # Basic Connection Tests
    # =====================================================================

    def test_connect_adds_user(self, manager):
        """Test that connect() adds a user connection."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        assert "user1" in manager._user_connections
        assert manager._user_connections["user1"] == ws

    def test_connect_sets_heartbeat(self, manager):
        """Test that connect() sets heartbeat timestamp."""
        ws = self._make_websocket()
        before = datetime.now(timezone.utc)
        asyncio.run(manager.connect("user1", ws))
        after = datetime.now(timezone.utc)
        assert before <= manager._last_heartbeat["user1"] <= after

    def test_disconnect_removes_user(self, manager):
        """Test that disconnect() removes a user."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        asyncio.run(manager.disconnect("user1"))
        assert "user1" not in manager._user_connections

    def test_disconnect_nonexistent_user(self, manager):
        """Test that disconnect() handles nonexistent user gracefully."""
        asyncio.run(manager.disconnect("nonexistent"))
        assert True  # Should not raise

    def test_disconnect_removes_user_from_room(self, manager):
        """Test that disconnect() removes user from room."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        asyncio.run(manager.join_room("user1", "room1"))
        asyncio.run(manager.disconnect("user1"))
        assert "user1" not in manager._user_room

    # =====================================================================
    # Heartbeat Tests
    # =====================================================================

    def test_update_heartbeat(self, manager):
        """Test that update_heartbeat() updates the timestamp."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        old_time = manager._last_heartbeat["user1"]
        asyncio.run(asyncio.sleep(0.01))
        asyncio.run(manager.update_heartbeat("user1"))
        new_time = manager._last_heartbeat["user1"]
        assert new_time >= old_time

    def test_update_heartbeat_nonexistent_user(self, manager):
        """Test that update_heartbeat() ignores nonexistent users."""
        asyncio.run(manager.update_heartbeat("nonexistent"))
        assert True  # Should not raise

    # =====================================================================
    # Room Management Tests
    # =====================================================================

    def test_join_room(self, manager):
        """Test that join_room() adds user to room."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        asyncio.run(manager.join_room("user1", "room1"))
        assert manager._user_room["user1"] == "room1"
        assert "user1" in manager._room_members["room1"]

    def test_join_room_twice_same_room(self, manager):
        """Test that join_room() handles rejoining same room."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        asyncio.run(manager.join_room("user1", "room1"))
        asyncio.run(manager.join_room("user1", "room1"))
        assert manager._user_room["user1"] == "room1"
        assert "user1" in manager._room_members["room1"]

    def test_join_room_switches_rooms(self, manager):
        """Test that join_room() switches rooms correctly."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        asyncio.run(manager.join_room("user1", "room1"))
        asyncio.run(manager.join_room("user1", "room2"))
        assert manager._user_room["user1"] == "room2"
        assert "user1" not in manager._room_members.get("room1", set())
        assert "user1" in manager._room_members["room2"]

    def test_exit_room(self, manager):
        """Test that exit_room() removes user from room."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        asyncio.run(manager.join_room("user1", "room1"))
        asyncio.run(manager.exit_room("user1"))
        assert "user1" not in manager._user_room
        assert manager._room_members.get("room1") is None

    def test_exit_room_nonexistent_user(self, manager):
        """Test that exit_room() handles nonexistent user."""
        asyncio.run(manager.exit_room("nonexistent"))
        assert True  # Should not raise

    def test_exit_room_cleans_up_empty_room(self, manager):
        """Test that exit_room() cleans up empty rooms."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        asyncio.run(manager.join_room("user1", "room1"))
        asyncio.run(manager.exit_room("user1"))
        assert "room1" not in manager._room_members

    # =====================================================================
    # Broadcast Tests
    # =====================================================================

    def test_send_to_user(self, manager):
        """Test that send_to_user() sends message to user."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        payload = {"action": "test"}
        asyncio.run(manager.send_to_user("user1", payload))
        ws.send_json.assert_awaited_once_with(payload)

    def test_send_to_nonexistent_user(self, manager):
        """Test that send_to_user() handles nonexistent user."""
        payload = {"action": "test"}
        asyncio.run(manager.send_to_user("nonexistent", payload))
        assert True  # Should not raise

    def test_broadcast_to_room(self, manager):
        """Test that broadcast_to_room() broadcasts to all room members."""
        ws1 = self._make_websocket()
        ws2 = self._make_websocket()
        asyncio.run(manager.connect("user1", ws1))
        asyncio.run(manager.connect("user2", ws2))
        asyncio.run(manager.join_room("user1", "room1"))
        asyncio.run(manager.join_room("user2", "room1"))
        payload = {"action": "broadcast"}
        asyncio.run(manager.broadcast_to_room("room1", payload))
        ws1.send_json.assert_awaited_once_with(payload)
        ws2.send_json.assert_awaited_once_with(payload)

    def test_broadcast_to_empty_room(self, manager):
        """Test that broadcast_to_room() handles empty rooms."""
        payload = {"action": "broadcast"}
        asyncio.run(manager.broadcast_to_room("empty_room", payload))
        assert True  # Should not raise

    # =====================================================================
    # Getter Tests
    # =====================================================================

    def test_get_user_room(self, manager):
        """Test that get_user_room() returns user's room."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        asyncio.run(manager.join_room("user1", "room1"))
        room = asyncio.run(manager.get_user_room("user1"))
        assert room == "room1"

    def test_get_user_room_nonexistent(self, manager):
        """Test that get_user_room() returns None for nonexistent user."""
        room = asyncio.run(manager.get_user_room("nonexistent"))
        assert room is None

    def test_get_room_members(self, manager):
        """Test that get_room_members() returns room members."""
        ws1 = self._make_websocket()
        ws2 = self._make_websocket()
        asyncio.run(manager.connect("user1", ws1))
        asyncio.run(manager.connect("user2", ws2))
        asyncio.run(manager.join_room("user1", "room1"))
        asyncio.run(manager.join_room("user2", "room1"))
        members = asyncio.run(manager.get_room_members("room1"))
        assert members == {"user1", "user2"}

    def test_get_room_members_empty(self, manager):
        """Test that get_room_members() returns empty set for nonexistent room."""
        members = asyncio.run(manager.get_room_members("nonexistent"))
        assert members == set()

    def test_get_user_connection(self, manager):
        """Test that get_user_connection() returns user's websocket."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        conn = asyncio.run(manager.get_user_connection("user1"))
        assert conn == ws

    def test_get_user_connection_nonexistent(self, manager):
        """Test that get_user_connection() returns None for nonexistent user."""
        conn = asyncio.run(manager.get_user_connection("nonexistent"))
        assert conn is None

    # =====================================================================
    # Static Method Tests
    # =====================================================================

    def test_room_channel(self):
        """Test that _room_channel() creates correct channel name."""
        channel = ConnectionManager._room_channel("room123")
        assert channel == "chat:room:room123"

    def test_channel_room_id(self):
        """Test that _channel_room_id() extracts room ID from channel."""
        room_id = ConnectionManager._channel_room_id("chat:room:room123")
        assert room_id == "room123"

    def test_channel_room_id_invalid_channel(self):
        """Test that _channel_room_id() returns None for invalid channel."""
        room_id = ConnectionManager._channel_room_id("invalid:channel")
        assert room_id is None

    def test_channel_room_id_none_input(self):
        """Test that _channel_room_id() returns None for None input."""
        room_id = ConnectionManager._channel_room_id(None)
        assert room_id is None

    # =====================================================================
    # Cleanup Tests
    # =====================================================================

    def test_cleanup_stale_connections(self, manager):
        """Test that _cleanup_stale_connections() removes stale users."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        # Manually set heartbeat to old time
        old_time = datetime.now(timezone.utc) - timedelta(seconds=200)
        manager._last_heartbeat["user1"] = old_time
        asyncio.run(manager._cleanup_stale_connections())
        assert "user1" not in manager._user_connections

    def test_cleanup_keeps_recent_connections(self, manager):
        """Test that _cleanup_stale_connections() keeps recent connections."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        asyncio.run(manager._cleanup_stale_connections())
        assert "user1" in manager._user_connections

    def test_cleanup_closes_stale_sockets(self, manager):
        """Test that _cleanup_stale_connections() closes stale sockets."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        old_time = datetime.now(timezone.utc) - timedelta(seconds=200)
        manager._last_heartbeat["user1"] = old_time
        asyncio.run(manager._cleanup_stale_connections())
        ws.close.assert_awaited_once()

    def test_cleanup_stale_connections_in_room(self, manager):
        """Test that _cleanup_stale_connections() cleans up room memberships."""
        ws = self._make_websocket()
        asyncio.run(manager.connect("user1", ws))
        asyncio.run(manager.join_room("user1", "room1"))
        old_time = datetime.now(timezone.utc) - timedelta(seconds=200)
        manager._last_heartbeat["user1"] = old_time
        asyncio.run(manager._cleanup_stale_connections())
        assert "user1" not in manager._user_room
        assert manager._room_members.get("room1") is None

    # =====================================================================
    # Initialization Tests
    # =====================================================================

    def test_init_raises_without_session_local(self):
        """Test that __init__() raises if SessionLocal is None."""
        with patch("backend.console.handler_ws.connection_manager.SessionLocal", None):
            with pytest.raises(RuntimeError):
                ConnectionManager()

    def test_utcnow(self, manager):
        """Test that _utcnow() returns UTC datetime."""
        now = manager._utcnow()
        assert now.tzinfo == timezone.utc
        assert isinstance(now, datetime)
