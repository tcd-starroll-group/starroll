import asyncio
import hashlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import reset_password as reset_module


def test_reset_password_email_not_found(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(reset_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(reset_module.User, "get_by_email",
                        staticmethod(lambda db, email: None))

    payload = SimpleNamespace(email="no@x.com", code="1234", new_password="p")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(reset_module.api_reset_password_post(payload))

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Email not found"


def test_reset_password_invalid_code(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(reset_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(reset_module.User, "get_by_email", staticmethod(
        lambda db, email: SimpleNamespace(email=email)))
    monkeypatch.setattr(reset_module, "verification_code_store", SimpleNamespace(
        verify_verification_code=lambda e, c: False))

    payload = SimpleNamespace(email="me@x.com", code="bad", new_password="p")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(reset_module.api_reset_password_post(payload))

    assert exc_info.value.status_code == 400


def test_reset_password_success_commits(monkeypatch: pytest.MonkeyPatch):
    committed = {}

    class Db:
        def commit(self):
            committed["ok"] = True

    class Ctx:
        def __enter__(self):
            return Db()

        def __exit__(self, exc_type, exc, tb):
            return False

    def _update(db, email, new_hash):
        committed["hash"] = new_hash

    monkeypatch.setattr(reset_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(reset_module.User, "get_by_email", staticmethod(
        lambda db, email: SimpleNamespace(email=email)))
    monkeypatch.setattr(reset_module, "verification_code_store", SimpleNamespace(
        verify_verification_code=lambda e, c: True))
    monkeypatch.setattr(reset_module.User,
                        "update_password_by_email", staticmethod(_update))

    payload = SimpleNamespace(
        email="me@x.com", code="ok", new_password="secret")
    result = asyncio.run(reset_module.api_reset_password_post(payload))

    assert isinstance(result, dict)
    assert result.get("message") == "Password reset successfully"
    assert committed.get("ok") is True
    # hash should be sha256 of "secret"
    assert committed.get("hash") == hashlib.sha256(b"secret").hexdigest()
