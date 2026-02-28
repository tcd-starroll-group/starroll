import asyncio
import hashlib
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import reset_password_send_code as reset_password_send_code_module
from backend.console.handler import reset_password as reset_password_module
from backend.console.handler.reset_password_send_code import api_reset_password_send_code_post
from backend.console.handler.reset_password import api_reset_password_post
from backend.console.dal.rds.user import User
from gen.py.src.openapi_server.models.reset_password_send_code_request import ResetPasswordSendCodeRequest
from gen.py.src.openapi_server.models.reset_password_request import ResetPasswordRequest


# ============================================================
# Endpoint 1: POST /api/resetPasswordSendCode
# Flow: validate email + username -> generate code -> save to Redis -> send email
# ============================================================

def test_send_code_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """Happy path: email exists and username matches, verification code should be sent."""
    User.create(db_session, "alice", hashlib.sha256("pass".encode()).hexdigest(), "alice@example.com")

    monkeypatch.setattr(reset_password_send_code_module, "get_db", lambda: iter([db_session]))
    monkeypatch.setattr(
        reset_password_send_code_module.verification_code_store,
        "generate_verification_code",
        lambda: "654321"
    )
    monkeypatch.setattr(
        reset_password_send_code_module.verification_code_store,
        "save_verification_code",
        lambda email, code: None
    )
    monkeypatch.setattr(
        reset_password_send_code_module,
        "send_verification_email",
        lambda email, code: True
    )

    payload = ResetPasswordSendCodeRequest(email="alice@example.com", userName="alice")
    result = asyncio.run(api_reset_password_send_code_post(payload))
    assert result["message"] == "Verification code sent successfully"


def test_send_code_email_not_found(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """Email does not exist in the database, should return 404."""
    monkeypatch.setattr(reset_password_send_code_module, "get_db", lambda: iter([db_session]))

    payload = ResetPasswordSendCodeRequest(email="ghost@example.com", userName="ghost")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_reset_password_send_code_post(payload))
    assert exc_info.value.status_code == 404


def test_send_code_username_mismatch(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """Email exists but username does not match, should return 400."""
    User.create(db_session, "bob", hashlib.sha256("pass".encode()).hexdigest(), "bob@example.com")
    monkeypatch.setattr(reset_password_send_code_module, "get_db", lambda: iter([db_session]))

    payload = ResetPasswordSendCodeRequest(email="bob@example.com", userName="wrong_username")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_reset_password_send_code_post(payload))
    assert exc_info.value.status_code == 400


def test_send_code_email_send_failure(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """SMTP send fails, should return 500."""
    User.create(db_session, "carol", hashlib.sha256("pass".encode()).hexdigest(), "carol@example.com")
    monkeypatch.setattr(reset_password_send_code_module, "get_db", lambda: iter([db_session]))
    monkeypatch.setattr(
        reset_password_send_code_module.verification_code_store,
        "generate_verification_code",
        lambda: "111111"
    )
    monkeypatch.setattr(
        reset_password_send_code_module.verification_code_store,
        "save_verification_code",
        lambda email, code: None
    )
    monkeypatch.setattr(
        reset_password_send_code_module,
        "send_verification_email",
        lambda email, code: False
    )

    payload = ResetPasswordSendCodeRequest(email="carol@example.com", userName="carol")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_reset_password_send_code_post(payload))
    assert exc_info.value.status_code == 500


# ============================================================
# Endpoint 2: POST /api/resetPassword
# Flow: validate email -> verify code -> hash new password -> update database
# ============================================================

def test_reset_password_success(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """Happy path: correct verification code, password should be updated in the database."""
    old_hash = hashlib.sha256("old_pass".encode()).hexdigest()
    User.create(db_session, "dave", old_hash, "dave@example.com")

    monkeypatch.setattr(reset_password_module, "get_db", lambda: iter([db_session]))
    monkeypatch.setattr(
        reset_password_module.verification_code_store,
        "verify_verification_code",
        lambda email, code: code == "123456"
    )

    payload = ResetPasswordRequest(email="dave@example.com", code="123456", newPassword="new_pass_abc")
    result = asyncio.run(api_reset_password_post(payload))
    assert result["message"] == "Password reset successfully"

    user = User.get_by_email(db_session, "dave@example.com")
    expected_hash = hashlib.sha256("new_pass_abc".encode()).hexdigest()
    assert user.password == expected_hash


def test_reset_password_email_not_found(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """Email does not exist in the database, should return 404."""
    monkeypatch.setattr(reset_password_module, "get_db", lambda: iter([db_session]))

    payload = ResetPasswordRequest(email="nobody@example.com", code="123456", newPassword="new_pass")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_reset_password_post(payload))
    assert exc_info.value.status_code == 404


def test_reset_password_invalid_code(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    """Verification code is incorrect, should return 400."""
    old_hash = hashlib.sha256("pass".encode()).hexdigest()
    User.create(db_session, "eve", old_hash, "eve@example.com")

    monkeypatch.setattr(reset_password_module, "get_db", lambda: iter([db_session]))
    monkeypatch.setattr(
        reset_password_module.verification_code_store,
        "verify_verification_code",
        lambda email, code: False
    )

    payload = ResetPasswordRequest(email="eve@example.com", code="wrong_code", newPassword="new_pass")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(api_reset_password_post(payload))
    assert exc_info.value.status_code == 400