from backend.config import settings
import threading
import time


_EPOCH_MS = 1704067200000
_WORKER_ID_BITS = 10
_SEQUENCE_BITS = 12
_MAX_WORKER_ID = (1 << _WORKER_ID_BITS) - 1
_MAX_SEQUENCE = (1 << _SEQUENCE_BITS) - 1

_LOCK = threading.Lock()
_LAST_TIMESTAMP_MS = -1
_SEQUENCE = 0


def _current_timestamp_ms() -> int:
    return time.time_ns() // 1_000_000


def _wait_next_millisecond(last_timestamp_ms: int) -> int:
    current = _current_timestamp_ms()
    while current <= last_timestamp_ms:
        time.sleep(0.0001)
        current = _current_timestamp_ms()
    return current


def _resolve_worker_id() -> int:
    worker_id = int(settings.worker_id)
    if worker_id < 0 or worker_id > _MAX_WORKER_ID:
        raise ValueError(
            f"WORKER_ID out of range: {worker_id}, expected 0..{_MAX_WORKER_ID}"
        )
    return worker_id


def gen_snowflake_id() -> int:
    global _LAST_TIMESTAMP_MS, _SEQUENCE

    worker_id = _resolve_worker_id()
    with _LOCK:
        current_ms = _current_timestamp_ms()
        if current_ms < _LAST_TIMESTAMP_MS:
            current_ms = _wait_next_millisecond(_LAST_TIMESTAMP_MS)

        if current_ms == _LAST_TIMESTAMP_MS:
            _SEQUENCE = (_SEQUENCE + 1) & _MAX_SEQUENCE
            if _SEQUENCE == 0:
                current_ms = _wait_next_millisecond(_LAST_TIMESTAMP_MS)
        else:
            _SEQUENCE = 0

        _LAST_TIMESTAMP_MS = current_ms

        timestamp_part = (
            current_ms - _EPOCH_MS) << (_WORKER_ID_BITS + _SEQUENCE_BITS)
        worker_part = worker_id << _SEQUENCE_BITS
        return timestamp_part | worker_part | _SEQUENCE
