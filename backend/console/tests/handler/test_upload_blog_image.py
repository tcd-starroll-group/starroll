import asyncio
import base64
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import upload_blog_image as upload_module


def test_upload_blog_image_none_request():
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(upload_module.api_upload_blog_image_post(None))
    assert exc_info.value.status_code == 400


def test_upload_blog_image_missing_image(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(upload_module.auth_module, "get_current_user_id", lambda: "1")
    payload = SimpleNamespace(image=None)
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(upload_module.api_upload_blog_image_post(payload))
    assert exc_info.value.status_code == 400


def test_upload_blog_image_invalid_base64(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(upload_module.auth_module, "get_current_user_id", lambda: "1")
    payload = SimpleNamespace(image="not_valid_base64!!!")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(upload_module.api_upload_blog_image_post(payload))
    assert exc_info.value.status_code == 400


def test_upload_blog_image_upload_failure(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(upload_module.auth_module, "get_current_user_id", lambda: "1")
    monkeypatch.setattr(upload_module, "upload_bytes",
                        lambda **kw: (_ for _ in ()).throw(RuntimeError("minio down")))
    payload = SimpleNamespace(image=base64.b64encode(b"fake_image").decode())
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(upload_module.api_upload_blog_image_post(payload))
    assert exc_info.value.status_code == 500


def test_upload_blog_image_success(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(upload_module.auth_module, "get_current_user_id", lambda: "7")
    monkeypatch.setattr(upload_module, "upload_bytes", lambda **kw: None)
    monkeypatch.setattr(upload_module, "get_presigned_get_url",
                        lambda **kw: "http://minio/blog-images/7/test.jpg")

    payload = SimpleNamespace(image=base64.b64encode(b"fake_image").decode())
    result = asyncio.run(upload_module.api_upload_blog_image_post(payload))

    assert result.image_url == "http://minio/blog-images/7/test.jpg"
