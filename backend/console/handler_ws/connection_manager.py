from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import WebSocket
from pydantic import ValidationError

from backend.console.dal import get_redis_client
from backend.console.dal.rds.client import SessionLocal
from backend.console.dal.cache.client import RedisPubSubListener
from backend.console.handler_ws.chat_message_formatter import build_chat_messages_action_from_event
from backend.model.chat import ChatMessageKafkaEvent


class ConnectionManager:
    def __init__(self) -> None:
        if SessionLocal is None:
            raise RuntimeError(
                "SessionLocal is not configured. Chat websocket service cannot start."
            )

        # user_id -> WebSocket
        self._user_connections: dict[str, WebSocket] = {}
        # room_id -> set[user_id]
        self._room_members: dict[str, set[str]] = defaultdict(set)
        # user_id -> room_id
        self._user_room: dict[str, str] = {}
        # user_id -> latest heartbeat timestamp(UTC)
        self._last_heartbeat: dict[str, datetime] = {}

        self._lock = asyncio.Lock()
        self._heartbeat_timeout_seconds = 180
        self._heartbeat_check_interval_seconds = 60
        self._heartbeat_checker_task: asyncio.Task[None] | None = None
        self._pubsub_listener: RedisPubSubListener | None = None
        self._pubsub_listener_task: asyncio.Task[None] | None = None
        self._pubsub_retry_interval_seconds = 5

    @staticmethod
    def _room_channel(room_id: str) -> str:
        return f"chat:room:{room_id}"

    @staticmethod
    def _channel_room_id(channel: str) -> str | None:
        prefix = "chat:room:"
        if not isinstance(channel, str) or not channel.startswith(prefix):
            return None
        return channel[len(prefix):]

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    def _ensure_heartbeat_checker_started(self) -> None:
        if self._heartbeat_checker_task is not None and not self._heartbeat_checker_task.done():
            return
        self._heartbeat_checker_task = asyncio.create_task(
            self._heartbeat_checker_loop())

    def _ensure_pubsub_listener_started(self) -> None:
        if self._pubsub_listener is None:
            self._pubsub_listener = RedisPubSubListener(get_redis_client())

        if self._pubsub_listener_task is not None and not self._pubsub_listener_task.done():
            return
        self._pubsub_listener_task = asyncio.create_task(
            self._pubsub_listener_loop())

    async def _pubsub_listener_loop(self) -> None:
        while True:
            try:
                if self._pubsub_listener is None:
                    self._pubsub_listener = RedisPubSubListener(
                        get_redis_client())

                loop = asyncio.get_running_loop()

                def _message_handler(channel: str, message: str) -> None:
                    asyncio.run_coroutine_threadsafe(
                        self._handle_pubsub_message(channel, message), loop)

                await asyncio.to_thread(self._pubsub_listener.listen, _message_handler)
                print(
                    "Redis Pub/Sub listener returned unexpectedly; "
                    f"retrying in {self._pubsub_retry_interval_seconds}s..."
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(
                    "Redis Pub/Sub listener stopped unexpectedly: "
                    f"{exc}; retrying in {self._pubsub_retry_interval_seconds}s..."
                )

            await asyncio.sleep(self._pubsub_retry_interval_seconds)

    async def _handle_pubsub_message(self, channel: str, message: str) -> None:
        room_id = self._channel_room_id(channel)
        if room_id is None:
            return

        try:
            event = ChatMessageKafkaEvent.model_validate_json(message)
        except ValidationError as exc:
            print(f"Invalid chat event payload on channel={channel}: {exc}")
            return

        with SessionLocal() as db:
            payload = build_chat_messages_action_from_event(
                db, event).model_dump()

        await self.broadcast_to_room(room_id, payload)

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            self._user_connections[user_id] = websocket
            self._last_heartbeat[user_id] = self._utcnow()

        self._ensure_heartbeat_checker_started()

    async def disconnect(self, user_id: str) -> None:
        channel_to_unsubscribe: str | None = None
        async with self._lock:
            room_id = self._user_room.pop(user_id, None)
            if room_id is not None:
                self._room_members[room_id].discard(user_id)
                if not self._room_members[room_id]:
                    del self._room_members[room_id]
                    channel_to_unsubscribe = self._room_channel(room_id)
            self._user_connections.pop(user_id, None)
            self._last_heartbeat.pop(user_id, None)

        if channel_to_unsubscribe is not None and self._pubsub_listener is not None:
            self._pubsub_listener.unsubscribe([channel_to_unsubscribe])

    async def update_heartbeat(self, user_id: str) -> None:
        async with self._lock:
            if user_id in self._user_connections:
                self._last_heartbeat[user_id] = self._utcnow()

    async def join_room(self, user_id: str, room_id: str) -> None:
        channel_to_subscribe: str | None = None
        old_channel_to_unsubscribe: str | None = None
        async with self._lock:
            old_room_id = self._user_room.get(user_id)
            if old_room_id == room_id:
                return

            if old_room_id is not None:
                self._room_members[old_room_id].discard(user_id)
                if not self._room_members[old_room_id]:
                    del self._room_members[old_room_id]
                    old_channel_to_unsubscribe = self._room_channel(
                        old_room_id)

            self._user_room[user_id] = room_id
            should_subscribe = len(self._room_members[room_id]) == 0
            self._room_members[room_id].add(user_id)
            if should_subscribe:
                channel_to_subscribe = self._room_channel(room_id)

        if old_channel_to_unsubscribe is not None and self._pubsub_listener is not None:
            self._pubsub_listener.unsubscribe([old_channel_to_unsubscribe])

        if channel_to_subscribe is not None:
            self._ensure_pubsub_listener_started()
            if self._pubsub_listener is not None:
                self._pubsub_listener.subscribe([channel_to_subscribe])

    async def exit_room(self, user_id: str) -> None:
        channel_to_unsubscribe: str | None = None
        async with self._lock:
            room_id = self._user_room.pop(user_id, None)
            if room_id is None:
                return

            self._room_members[room_id].discard(user_id)
            if not self._room_members[room_id]:
                del self._room_members[room_id]
                channel_to_unsubscribe = self._room_channel(room_id)

        if channel_to_unsubscribe is not None and self._pubsub_listener is not None:
            self._pubsub_listener.unsubscribe([channel_to_unsubscribe])

    async def get_user_room(self, user_id: str) -> str | None:
        async with self._lock:
            return self._user_room.get(user_id)

    async def get_room_members(self, room_id: str) -> set[str]:
        async with self._lock:
            return set(self._room_members.get(room_id, set()))

    async def get_user_connection(self, user_id: str) -> WebSocket | None:
        async with self._lock:
            return self._user_connections.get(user_id)

    async def send_to_user(self, user_id: str, payload: dict) -> None:
        websocket = await self.get_user_connection(user_id)
        if websocket is None:
            return
        await websocket.send_json(payload)

    async def broadcast_to_room(self, room_id: str, payload: dict) -> None:
        async with self._lock:
            member_ids = list(self._room_members.get(room_id, set()))
            sockets = [self._user_connections[user_id]
                       for user_id in member_ids if user_id in self._user_connections]

        for websocket in sockets:
            await websocket.send_json(payload)

    async def _heartbeat_checker_loop(self) -> None:
        while True:
            await asyncio.sleep(self._heartbeat_check_interval_seconds)
            await self._cleanup_stale_connections()

    async def _cleanup_stale_connections(self) -> None:
        now = self._utcnow()
        timeout_delta = timedelta(seconds=self._heartbeat_timeout_seconds)

        channels_to_unsubscribe: list[str] = []
        async with self._lock:
            stale_user_ids = [
                user_id
                for user_id, heartbeat_time in self._last_heartbeat.items()
                if now - heartbeat_time >= timeout_delta
            ]

            stale_sockets: list[WebSocket] = []
            for user_id in stale_user_ids:
                room_id = self._user_room.pop(user_id, None)
                if room_id is not None:
                    self._room_members[room_id].discard(user_id)
                    if not self._room_members[room_id]:
                        del self._room_members[room_id]
                        channels_to_unsubscribe.append(
                            self._room_channel(room_id))

                socket = self._user_connections.pop(user_id, None)
                if socket is not None:
                    stale_sockets.append(socket)

                self._last_heartbeat.pop(user_id, None)

        if channels_to_unsubscribe and self._pubsub_listener is not None:
            self._pubsub_listener.unsubscribe(channels_to_unsubscribe)

        for socket in stale_sockets:
            try:
                await socket.close()
            except Exception:
                pass
