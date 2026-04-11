from __future__ import annotations

import json
import os
import random
import threading
import time
from typing import Any

import websocket  # websocket-client
from locust import HttpUser, between, events, task
from locust.exception import StopUser


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MIN_USER_INDEX = 1
MAX_USER_INDEX = 100_000
HEARTBEAT_INTERVAL = 10   # seconds
USER_LIFETIME_MIN = 60    # seconds – minimum time a user stays connected
USER_LIFETIME_MAX = 90    # seconds – maximum time a user stays connected
ROOM_SWITCH_CHANCE = 0.1  # 10 % chance to switch rooms each task tick
WS_TIMEOUT = 10           # seconds – websocket receive timeout
HTTP_PREFIX = ""          # leave empty; HttpUser base_url is used for HTTP
WS_CONNECT_RETRIES = 4    # how many times to retry a failed WS connect
WS_CONNECT_BACKOFF = 2.0  # seconds – initial back-off; doubles each attempt

# Load room IDs from room_ids.json (located next to this script)
_ROOM_IDS_FILE = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "room_ids.json")
with open(_ROOM_IDS_FILE, encoding="utf-8") as _f:
    ROOM_IDS: list[int] = json.load(_f)["room_ids"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _random_room_id(exclude=None) -> int:
    room_id = random.choice(ROOM_IDS)
    if exclude is not None and len(ROOM_IDS) > 1:
        while room_id == exclude:
            room_id = random.choice(ROOM_IDS)
    return room_id


# ---------------------------------------------------------------------------
# Global user-index pool – prevents duplicate concurrent logins
# ---------------------------------------------------------------------------

_USER_INDEX_LOCK = threading.Lock()
_USER_INDEX_IN_USE: set[int] = set()


def _claim_user_index() -> int:
    """Return a random user index that is not currently in use."""
    with _USER_INDEX_LOCK:
        total = MAX_USER_INDEX - MIN_USER_INDEX + 1
        if len(_USER_INDEX_IN_USE) >= total:
            # Exhausted – pick any and register it to avoid silent duplicates
            index = random.randint(MIN_USER_INDEX, MAX_USER_INDEX)
            _USER_INDEX_IN_USE.add(index)
            return index
        while True:
            index = random.randint(MIN_USER_INDEX, MAX_USER_INDEX)
            if index not in _USER_INDEX_IN_USE:
                _USER_INDEX_IN_USE.add(index)
                return index


def _release_user_index(index: int) -> None:
    with _USER_INDEX_LOCK:
        _USER_INDEX_IN_USE.discard(index)


# ---------------------------------------------------------------------------
# WebSocket wrapper (synchronous websocket-client in a background thread)
# ---------------------------------------------------------------------------

class ChatWebSocket:
    """Thin wrapper around websocket-client for use inside a Locust task."""

    def __init__(self, ws_url: str, token: str, on_error=None) -> None:
        self._url = f"{ws_url}?token={token}"
        self._on_error = on_error
        self._ws: websocket.WebSocket | None = None
        self._lock = threading.Lock()
        self._closed = False

    def connect(self) -> None:
        self._ws = websocket.create_connection(
            self._url,
            timeout=WS_TIMEOUT,
        )
        self._closed = False

    def send(self, payload: dict[str, Any]) -> None:
        if self._closed or self._ws is None:
            return
        with self._lock:
            try:
                self._ws.send(json.dumps(payload))
            except Exception as exc:  # noqa: BLE001
                self._closed = True
                if self._on_error:
                    self._on_error(exc)

    def receive(self) -> dict[str, Any] | None:
        """Receive one message under the send/recv lock to prevent races."""
        if self._closed or self._ws is None:
            return None
        with self._lock:
            try:
                raw = self._ws.recv()
                if raw:
                    return json.loads(raw)
            except websocket.WebSocketTimeoutException:
                pass
            except Exception as exc:  # noqa: BLE001
                self._closed = True
                if self._on_error:
                    self._on_error(exc)
            return None

    def send_and_receive(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        """Atomically send a message and receive one response under the lock.

        This prevents the heartbeat thread from interleaving recv() calls
        with task-thread recv() calls and reading each other's messages.
        """
        if self._closed or self._ws is None:
            return None
        with self._lock:
            try:
                self._ws.send(json.dumps(payload))
            except Exception as exc:  # noqa: BLE001
                self._closed = True
                if self._on_error:
                    self._on_error(exc)
                return None
            try:
                raw = self._ws.recv()
                if raw:
                    return json.loads(raw)
            except websocket.WebSocketTimeoutException:
                pass
            except Exception as exc:  # noqa: BLE001
                self._closed = True
                if self._on_error:
                    self._on_error(exc)
            return None

    def drain(self, max_messages: int = 20) -> None:
        """Drain up to *max_messages* pending server-push messages under the lock.

        The server may push N historical messages after JoinChatRoom.  Without
        draining them they would be read by the next send_and_receive() call as
        if they were the response to that action, skewing latency stats.
        """
        if self._closed or self._ws is None:
            return
        with self._lock:
            for _ in range(max_messages):
                if self._closed or self._ws is None:
                    break
                try:
                    raw = self._ws.recv()
                    if not raw:
                        break
                except websocket.WebSocketTimeoutException:
                    break
                except Exception:  # noqa: BLE001
                    break

    def close(self) -> None:
        self._closed = True
        if self._ws is not None:
            try:
                self._ws.close()
            except Exception:  # noqa: BLE001
                pass
            self._ws = None

    @property
    def is_closed(self) -> bool:
        return self._closed


# ---------------------------------------------------------------------------
# Locust User
# ---------------------------------------------------------------------------

class ChatUser(HttpUser):
    """
    Simulates a single chat user:
      - login via HTTP → token
      - WebSocket lifecycle (join room, send messages, heartbeat, switch rooms)
    """

    wait_time = between(5, 10)

    # ------------------------------------------------------------------ setup

    def on_start(self) -> None:
        # Ensure base_url has a scheme (in case --host was given without one)
        if not self.client.base_url.startswith(("http://", "https://")):
            self.client.base_url = "http://" + self.client.base_url

        index = _claim_user_index()
        self._user_index = index
        self._username = f"test_user_{index}"
        self._password = f"test_user_{index}"
        self._token: str = ""
        self._ws: ChatWebSocket | None = None
        self._current_room: int | None = None
        self._last_heartbeat: float = 0.0
        self._message_seq: int = 0
        self._start_time: float = time.time()
        self._lifetime: float = random.uniform(
            USER_LIFETIME_MIN, USER_LIFETIME_MAX)

        self._heartbeat_stop = threading.Event()
        self._heartbeat_thread: threading.Thread | None = None
        self._lifetime_expired: bool = False
        # Set by _on_ws_error so the next task boundary stops the user quickly
        # instead of drifting through the full wait_time with a dead connection.
        self._ws_error_flag: bool = False

        self._login()
        self._connect_ws()
        self._start_heartbeat_thread()

    def on_stop(self) -> None:
        self._heartbeat_stop.set()
        if self._heartbeat_thread is not None and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=HEARTBEAT_INTERVAL + 2)
        self._safe_ws_close()
        _release_user_index(self._user_index)

    # ------------------------------------------------- heartbeat thread

    def _start_heartbeat_thread(self) -> None:
        self._heartbeat_stop.clear()

        def _loop() -> None:
            while not self._heartbeat_stop.wait(timeout=HEARTBEAT_INTERVAL):
                if self._ws is None or self._ws.is_closed:
                    break
                if time.time() - self._start_time >= self._lifetime:
                    # Signal the Locust scheduler to stop this user
                    self._heartbeat_stop.set()
                    self.environment.runner.send_message  # keep reference alive
                    # StopUser can only be raised from the main greenlet; set a
                    # flag that _check_lifetime() will honour on the next tick.
                    self._lifetime_expired = True
                    break
                try:
                    self._heartbeat()
                except Exception:  # noqa: BLE001
                    break

        self._heartbeat_thread = threading.Thread(target=_loop, daemon=True)
        self._heartbeat_thread.start()

    def _check_lifetime(self) -> None:
        """Raise StopUser once this user has lived past its lifetime, or when
        the WebSocket has silently died so the dead greenlet is not counted as
        an active connection by Locust."""
        if (
            self._lifetime_expired
            or self._ws_error_flag
            or time.time() - self._start_time >= self._lifetime
        ):
            raise StopUser()

    # ----------------------------------------------------------------- login

    def _login(self) -> None:
        with self.client.post(
            "/api/userLogin",
            json={"username": self._username, "password": self._password},
            catch_response=True,
            name="/api/userLogin",
        ) as resp:
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    # TokenResponse – adjust key name if different in your schema
                    self._token = (
                        data.get("token")
                        or data.get("access_token")
                        or data.get("data", {}).get("token")
                        or ""
                    )
                    if not self._token:
                        resp.failure(
                            f"No token in response: user={self._username} body={data}"
                        )
                        raise StopUser()
                    resp.success()
                except StopUser:
                    raise
                except Exception as exc:  # noqa: BLE001
                    resp.failure(
                        f"Failed to parse login response: user={self._username} "
                        f"exc={type(exc).__name__}: {exc} body={resp.text!r}"
                    )
                    raise StopUser() from exc
            else:
                resp.failure(
                    f"Login failed [{resp.status_code}] user={self._username} "
                    f"body={resp.text!r}"
                )
                raise StopUser()

    # ------------------------------------------------------------ websocket

    def _ws_url(self) -> str:
        """Convert http(s) base_url to ws(s)."""
        base = self.client.base_url.rstrip("/")
        if base.startswith("https://"):
            return base.replace("https://", "wss://", 1) + "/api/chat"
        if base.startswith("http://"):
            return base.replace("http://", "ws://", 1) + "/api/chat"
        return "ws://" + base + "/api/chat"

    def _connect_ws(self) -> None:
        """Connect to the WebSocket endpoint with exponential-backoff retries.

        Retrying here (rather than immediately raising StopUser) avoids the
        rapid stop→respawn→fail cycle that occurs when the server is briefly
        unable to accept new connections under heavy load.  Without retries,
        every expiring user spawns a replacement that dies instantly in
        on_start(), so Locust's displayed count stays at the target while the
        real connection count falls below it.
        """
        url = self._ws_url()
        self._ws = ChatWebSocket(
            url,
            self._token,
            on_error=self._on_ws_error,
        )

        last_exc: Exception | None = None
        backoff = WS_CONNECT_BACKOFF
        for attempt in range(WS_CONNECT_RETRIES + 1):
            start = time.time()
            try:
                self._ws.connect()
                elapsed_ms = int((time.time() - start) * 1000)
                events.request.fire(
                    request_type="WSS",
                    name="ws_connect",
                    response_time=elapsed_ms,
                    response_length=0,
                    exception=None,
                    context=self.context(),
                )
                break  # success
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                elapsed_ms = int((time.time() - start) * 1000)
                if attempt < WS_CONNECT_RETRIES:
                    # Record the transient failure but don't stop the user yet.
                    events.request.fire(
                        request_type="WSS",
                        name="ws_connect_retry",
                        response_time=elapsed_ms,
                        response_length=0,
                        exception=exc,
                        context=self.context(),
                    )
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 30.0)  # cap at 30 s
                else:
                    # All retries exhausted – give up and record as a failure.
                    events.request.fire(
                        request_type="WSS",
                        name="ws_connect",
                        response_time=elapsed_ms,
                        response_length=0,
                        exception=exc,
                        context=self.context(),
                    )
                    raise StopUser() from exc

        # Join an initial room right after connecting
        self._join_room(_random_room_id())

    def _on_ws_error(self, exc: Exception) -> None:
        # Mark the error so _check_lifetime() stops this user on the next task
        # boundary.  Without this flag the Locust greenlet keeps sleeping
        # through wait_time while holding no real WS connection, which makes
        # Locust's user count higher than the actual server-side connections.
        self._ws_error_flag = True
        events.request.fire(
            request_type="WSS",
            name="ws_error",
            response_time=0,
            response_length=0,
            exception=exc,
            context=self.context(),
        )

    def _safe_ws_close(self) -> None:
        if self._ws is not None:
            self._ws.close()
            self._ws = None

    # ------------------------------------------------- WebSocket actions

    # Number of times a transient WS error is retried before giving up
    _WS_MAX_RETRIES = 2

    def _ws_send(self, action_name: str, payload: dict[str, Any]) -> None:
        """Send a WS action, read one response, and record in Locust statistics.

        Uses send_and_receive() so that the heartbeat thread cannot interleave
        its own recv() call with ours.

        Transient exceptions are retried up to _WS_MAX_RETRIES times before
        raising StopUser, to avoid a cascade of user-exits on short server
        hiccups.  If the server replies with an ErrorAction the request is
        recorded as a failure but the user is kept alive.
        """
        if self._ws is None or self._ws.is_closed:
            raise StopUser()

        last_exc: Exception | None = None
        for attempt in range(self._WS_MAX_RETRIES + 1):
            start = time.time()
            error_msg: str | None = None
            try:
                response = self._ws.send_and_receive(payload)
                if isinstance(response, dict) and response.get("action") == "Error":
                    error_msg = (
                        f"ErrorAction: {response.get('message', '(no message)')}"
                        f" | action={action_name} payload={payload}"
                    )
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                elapsed_ms = int((time.time() - start) * 1000)
                if attempt < self._WS_MAX_RETRIES:
                    time.sleep(0.5 * (attempt + 1))  # brief back-off
                    continue
                # All retries exhausted
                detailed = Exception(
                    f"{type(exc).__name__}: {exc}"
                    f" | action={action_name} payload={payload}"
                    f" (after {attempt + 1} attempt(s))"
                )
                events.request.fire(
                    request_type="WSS",
                    name=f"ws_{action_name}",
                    response_time=elapsed_ms,
                    response_length=0,
                    exception=detailed,
                    context=self.context(),
                )
                raise StopUser() from exc
            else:
                elapsed_ms = int((time.time() - start) * 1000)
                break  # success path – fall through to reporting
        else:
            # Should not be reached, but guard anyway
            raise StopUser()

        if error_msg is not None:
            events.request.fire(
                request_type="WSS",
                name=f"ws_{action_name}",
                response_time=elapsed_ms,
                response_length=0,
                exception=Exception(error_msg),
                context=self.context(),
            )
            return

        events.request.fire(
            request_type="WSS",
            name=f"ws_{action_name}",
            response_time=elapsed_ms,
            response_length=0,
            exception=None,
            context=self.context(),
        )

    def _join_room(self, room_id: int) -> None:
        # JoinChatRoomAction: action, ChatRoomID (int), SinceMessageID (optional)
        self._ws_send(
            "JoinChatRoom",
            {"action": "JoinChatRoom", "ChatRoomID": room_id},
        )
        self._current_room = room_id
        # Drain any historical messages pushed by the server after the join so
        # that subsequent send_and_receive() calls see only fresh responses.
        if self._ws is not None:
            self._ws.drain()

    def _send_message(self, content: str) -> None:
        # SendMessageAction: action, message (str) — no room_id field
        self._ws_send(
            "SendMessage",
            {
                "action": "SendMessage",
                "message": content,
            },
        )

    def _list_messages(self) -> None:
        # ListMessagesAction: action, ChatRoomID (int), SinceMessageID (optional), Before (optional)
        self._ws_send(
            "ListMessages",
            {
                "action": "ListMessages",
                "ChatRoomID": self._current_room,
            },
        )

    def _heartbeat(self) -> None:
        # HeartBeatAction: action only
        self._ws_send(
            "HeartBeat",
            {"action": "HeartBeat"},
        )
        self._last_heartbeat = time.time()

    # ----------------------------------------------------------------- tasks

    @task(20)
    def task_send_message(self) -> None:
        """Main task: send a chat message."""
        self._check_lifetime()
        if self._ws is None or self._ws.is_closed:
            raise StopUser()

        # Ensure we are in a room
        if self._current_room is None:
            self._join_room(_random_room_id())

        # Possibly switch room first
        if random.random() < ROOM_SWITCH_CHANCE:
            old_room = self._current_room
            self._join_room(_random_room_id(exclude=old_room))

        self._message_seq += 1
        self._send_message(
            f"Hello from {self._username}, msg #{self._message_seq}"
        )

    @task(2)
    def task_list_messages(self) -> None:
        """List recent messages in current room."""
        self._check_lifetime()
        if self._ws is None or self._ws.is_closed:
            raise StopUser()

        if self._current_room is None:
            self._join_room(_random_room_id())

        self._list_messages()

    @task(2)
    def task_switch_room(self) -> None:
        """Explicitly switch to a different room."""
        self._check_lifetime()
        if self._ws is None or self._ws.is_closed:
            raise StopUser()

        self._join_room(_random_room_id(exclude=self._current_room))
