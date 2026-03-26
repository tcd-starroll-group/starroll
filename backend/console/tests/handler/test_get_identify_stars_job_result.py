import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.console.handler import get_identify_stars_job_result as job_module


def test_job_not_found(monkeypatch: pytest.MonkeyPatch):
    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(job_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(job_module.IdentifyStarsJobDAL,
                        "get_by_id", staticmethod(lambda db, jid: None))

    payload = SimpleNamespace(job_id="1")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(job_module.api_get_identify_stars_job_result_post(payload))

    assert exc_info.value.status_code != 200


def test_job_unauthorized(monkeypatch: pytest.MonkeyPatch):
    job = SimpleNamespace(id=2, user_id=10, result=None,
                          status="done", image_key=None, created_at=None)

    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(job_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(job_module, "get_current_user_id", lambda: 1)
    monkeypatch.setattr(job_module.IdentifyStarsJobDAL,
                        "get_by_id", staticmethod(lambda db, jid: job))

    payload = SimpleNamespace(job_id="2")
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(job_module.api_get_identify_stars_job_result_post(payload))

    assert exc_info.value.status_code == 403


def test_job_success_maps_result(monkeypatch: pytest.MonkeyPatch):
    data = {"calibration": {"ra": 1, "dec": 2, "radius": 3, "orientation": 4}, "stars": [
        {"names": ["A"], "pixelx": 5, "pixely": 6, "vmag": 1.2, "HIP": 123}]}
    job = SimpleNamespace(id=3, user_id=7, result=data,
                          status="done", image_key="k", created_at=None)

    class Ctx:
        def __enter__(self):
            return object()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(job_module, "db_context", lambda: Ctx())
    monkeypatch.setattr(job_module, "get_current_user_id", lambda: 7)
    monkeypatch.setattr(
        job_module,
        "get_presigned_get_url",
        lambda object_name, bucket_name: f"https://example.com/{bucket_name}/{object_name}",
    )
    monkeypatch.setattr(job_module.IdentifyStarsJobDAL,
                        "get_by_id", staticmethod(lambda db, jid: job))

    payload = SimpleNamespace(job_id="3")
    result = asyncio.run(
        job_module.api_get_identify_stars_job_result_post(payload))
    assert result is not None
    assert result.ori_image_url == "https://example.com/identify-stars/k"
