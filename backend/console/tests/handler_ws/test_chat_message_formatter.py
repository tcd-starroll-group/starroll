"""Unit tests for backend.console.handler_ws.chat_message_formatter"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from backend.console.handler_ws.chat_message_formatter import (
    build_chat_message_items,
    build_chat_messages_action,
    build_chat_messages_action_from_event,
)
from backend.model.chat import ChatMessageKafkaEvent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_message(user_id: int, message_id: int, message: str, created_at=None):
    """Return a minimal ChatMessages-like object."""
    m = MagicMock()
    m.user_id = user_id
    m.message_id = message_id
    m.message = message
    m.created_at = created_at or datetime(
        2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    return m


def _make_db(users: dict[int, str]):
    """Return a fake Session whose User.get_by_id returns usernames from dict."""
    db = MagicMock()
    return db


# ---------------------------------------------------------------------------
# build_chat_message_items
# ---------------------------------------------------------------------------

class TestBuildChatMessageItems:
    def test_empty_list(self, db_session):
        result = build_chat_message_items(db_session, [])
        assert result == []

    def test_single_message_with_user(self, db_session):
        from backend.console.dal.rds.user import User
        User.create(db_session, "alice", "pw", "alice@test.com")
        user = db_session.query(User).filter_by(username="alice").first()

        msg = _make_message(user_id=user.id, message_id=9999, message="hello")
        items = build_chat_message_items(db_session, [msg])
        assert len(items) == 1
        assert items[0].username == "alice"
        assert items[0].message == "hello"
        assert items[0].message_id == 9999

    def test_user_not_found_falls_back_to_str_id(self, db_session):
        """When user doesn't exist, username falls back to str(user_id)."""
        msg = _make_message(user_id=99999, message_id=1, message="hi")
        items = build_chat_message_items(db_session, [msg])
        assert items[0].username == "99999"

    def test_timestamp_from_datetime(self, db_session):
        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        msg = _make_message(user_id=99999, message_id=1,
                            message="t", created_at=ts)
        items = build_chat_message_items(db_session, [msg])
        assert items[0].timestamp == int(ts.timestamp())

    def test_timestamp_from_non_datetime_is_zero(self, db_session):
        msg = _make_message(user_id=99999, message_id=1,
                            message="t", created_at=None)
        # Override created_at to a non-datetime value
        msg.created_at = "not-a-datetime"
        items = build_chat_message_items(db_session, [msg])
        assert items[0].timestamp == 0

    def test_multiple_messages_same_user_cached(self, db_session):
        from backend.console.dal.rds.user import User
        User.create(db_session, "bob", "pw", "bob@test.com")
        user = db_session.query(User).filter_by(username="bob").first()

        msgs = [
            _make_message(user.id, 1, "msg1"),
            _make_message(user.id, 2, "msg2"),
        ]
        items = build_chat_message_items(db_session, msgs)
        assert len(items) == 2
        assert all(i.username == "bob" for i in items)

    def test_multiple_messages_different_users(self, db_session):
        from backend.console.dal.rds.user import User
        User.create(db_session, "u1", "pw", "u1@test.com")
        User.create(db_session, "u2", "pw", "u2@test.com")
        u1 = db_session.query(User).filter_by(username="u1").first()
        u2 = db_session.query(User).filter_by(username="u2").first()

        msgs = [
            _make_message(u1.id, 1, "from u1"),
            _make_message(u2.id, 2, "from u2"),
        ]
        items = build_chat_message_items(db_session, msgs)
        usernames = {i.username for i in items}
        assert usernames == {"u1", "u2"}


# ---------------------------------------------------------------------------
# build_chat_messages_action
# ---------------------------------------------------------------------------

class TestBuildChatMessagesAction:
    def test_returns_chat_messages_action(self, db_session):
        result = build_chat_messages_action(db_session, [])
        assert result.action == "ChatMessages"
        assert result.messages == []

    def test_returns_messages(self, db_session):
        from backend.console.dal.rds.user import User
        User.create(db_session, "carol", "pw", "carol@test.com")
        user = db_session.query(User).filter_by(username="carol").first()

        msg = _make_message(user.id, 42, "test message")
        result = build_chat_messages_action(db_session, [msg])
        assert result.action == "ChatMessages"
        assert len(result.messages) == 1
        assert result.messages[0].message == "test message"


# ---------------------------------------------------------------------------
# build_chat_messages_action_from_event
# ---------------------------------------------------------------------------

class TestBuildChatMessagesActionFromEvent:
    def test_user_exists(self, db_session):
        from backend.console.dal.rds.user import User
        User.create(db_session, "dave", "pw", "dave@test.com")
        user = db_session.query(User).filter_by(username="dave").first()

        event = ChatMessageKafkaEvent(
            user_id=user.id,
            chatroom_id=1,
            message_id=100,
            message="hello from event",
        )
        result = build_chat_messages_action_from_event(db_session, event)
        assert result.action == "ChatMessages"
        assert len(result.messages) == 1
        assert result.messages[0].username == "dave"
        assert result.messages[0].message == "hello from event"
        assert result.messages[0].message_id == 100

    def test_user_not_found_fallback(self, db_session):
        event = ChatMessageKafkaEvent(
            user_id=88888,
            chatroom_id=1,
            message_id=200,
            message="ghost message",
        )
        result = build_chat_messages_action_from_event(db_session, event)
        assert result.messages[0].username == "88888"
        assert result.messages[0].message == "ghost message"

    def test_timestamp_is_recent(self, db_session):
        from datetime import datetime, timezone
        before = int(datetime.now(timezone.utc).timestamp())
        event = ChatMessageKafkaEvent(
            user_id=99999, chatroom_id=2, message_id=1, message="ts test"
        )
        result = build_chat_messages_action_from_event(db_session, event)
        after = int(datetime.now(timezone.utc).timestamp())
        assert before <= result.messages[0].timestamp <= after + 1
