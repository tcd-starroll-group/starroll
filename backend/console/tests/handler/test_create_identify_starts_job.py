import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import create_identify_starts_job as create_module


def test_create_job_missing_fields():
    # missing user_id
    payload = SimpleNamespace(user_id=None, token="t", image="i")
    with pytest.raises(HTTPException):
        asyncio.run(create_module.api_create_identify_stars_job_post(payload))


def test_create_job_invalid_base64(monkeypatch: pytest.MonkeyPatch):
    payload = SimpleNamespace(user_id="1", token="t", image="not_base64")
    # verify_user_id_and_token should be callable but not raise
    monkeypatch.setattr(
        create_module, "verify_user_id_and_token", lambda t, u: None)
    with pytest.raises(HTTPException):
        asyncio.run(create_module.api_create_identify_stars_job_post(payload))


def test_create_job_success(monkeypatch: pytest.MonkeyPatch):
    # valid base64 of empty bytes
    import base64
    img = base64.b64encode(b"abc").decode()
    payload = SimpleNamespace(user_id="7", token="t", image=img)

    monkeypatch.setattr(
        create_module, "verify_user_id_and_token", lambda t, u: None)
    monkeypatch.setattr(create_module, "upload_bytes", lambda **kw: None)

    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(create_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(create_module.IdentifyStarsJob, "create",
                        staticmethod(lambda **kw: SimpleNamespace(id=55)))

    result = asyncio.run(
        create_module.api_create_identify_stars_job_post(payload))
    assert result.job_id == str(55)
