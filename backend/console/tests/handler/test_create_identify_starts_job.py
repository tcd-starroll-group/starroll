import asyncio
import base64
from unittest.mock import Mock, patch, MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import create_identify_starts_job as create_identify_starts_job_module
from backend.console.handler.create_identify_starts_job import api_create_identify_stars_job_post
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.constant import tos as tos_const
from backend.constant import star_identify as star_identify_const
from gen.py.src.openapi_server.models.api_create_identify_stars_job_post_request import ApiCreateIdentifyStarsJobPostRequest


class TestApiCreateIdentifyStarsJobPost:
    """Test cases for api_create_identify_stars_job_post handler."""

    def _create_valid_request(self, user_id="123", token="valid_token", image=None):
        """Helper to create a valid request."""
        if image is None:
            image = base64.b64encode(b"fake image data").decode()

        return ApiCreateIdentifyStarsJobPostRequest(
            user_id=user_id,
            token=token,
            image=image
        )

    def test_api_create_identify_stars_job_post_success(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test successful job creation with valid inputs."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass  # Mock successful verification

        def _upload_bytes_override(**kwargs):
            pass  # Mock successful upload

        monkeypatch.setattr(create_identify_starts_job_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            create_identify_starts_job_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )
        monkeypatch.setattr(
            create_identify_starts_job_module, "upload_bytes", _upload_bytes_override
        )

        # Execute
        request = self._create_valid_request()
        result = asyncio.run(api_create_identify_stars_job_post(request))

        # Verify
        assert result.job_id is not None
        assert result.job_id.isdigit()

        # Verify job was created in database
        job_id = int(result.job_id)
        job = IdentifyStarsJob.get_by_id(db_session, job_id)
        assert job is not None
        assert job.user_id == 123
        assert job.status == star_identify_const.STAR_IDENTIFY_JOB_STATUS_PENDING
        assert "123/" in job.image_key

    def test_api_create_identify_stars_job_post_missing_user_id(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test request with missing user_id."""
        def _get_db_override():
            yield db_session

        monkeypatch.setattr(create_identify_starts_job_module,
                            "get_db", _get_db_override)

        request = self._create_valid_request(user_id="")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_create_identify_stars_job_post(request))

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "userID is required"

    def test_api_create_identify_stars_job_post_missing_token(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test request with missing token."""
        def _get_db_override():
            yield db_session

        monkeypatch.setattr(create_identify_starts_job_module,
                            "get_db", _get_db_override)

        request = self._create_valid_request(token="")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_create_identify_stars_job_post(request))

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "token is required"

    def test_api_create_identify_stars_job_post_missing_image(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test request with missing image."""
        def _get_db_override():
            yield db_session

        monkeypatch.setattr(create_identify_starts_job_module,
                            "get_db", _get_db_override)

        request = self._create_valid_request(image="")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_create_identify_stars_job_post(request))

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "image is required"

    def test_api_create_identify_stars_job_post_invalid_token(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test request with invalid token."""
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            raise HTTPException(
                status_code=401, detail="Invalid or expired token")

        monkeypatch.setattr(create_identify_starts_job_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            create_identify_starts_job_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        request = self._create_valid_request(token="invalid_token")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_create_identify_stars_job_post(request))

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid or expired token"

    def test_api_create_identify_stars_job_post_token_user_id_mismatch(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test token belongs to different user."""
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            raise HTTPException(status_code=403, detail="User ID mismatch")

        monkeypatch.setattr(create_identify_starts_job_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            create_identify_starts_job_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        request = self._create_valid_request(user_id="123")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_create_identify_stars_job_post(request))

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "User ID mismatch"

    def test_api_create_identify_stars_job_post_invalid_base64_image(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test request with invalid base64 image data."""
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass  # Mock successful verification

        monkeypatch.setattr(create_identify_starts_job_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            create_identify_starts_job_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        request = self._create_valid_request(image="not_valid_base64!!!")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_create_identify_stars_job_post(request))

        assert exc_info.value.status_code == 400
        assert "Invalid base64 image data" in exc_info.value.detail

    def test_api_create_identify_stars_job_post_upload_failure(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test when MinIO upload fails."""
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass  # Mock successful verification

        def _upload_bytes_failure(**kwargs):
            raise Exception("MinIO connection failed")

        monkeypatch.setattr(create_identify_starts_job_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            create_identify_starts_job_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )
        monkeypatch.setattr(
            create_identify_starts_job_module, "upload_bytes", _upload_bytes_failure
        )

        request = self._create_valid_request()

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_create_identify_stars_job_post(request))

        assert exc_info.value.status_code == 500
        assert "Failed to upload image" in exc_info.value.detail

    def test_api_create_identify_stars_job_post_database_failure(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test when database save fails."""
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass  # Mock successful verification

        def _upload_bytes_override(**kwargs):
            pass  # Mock successful upload

        # Mock the IdentifyStarsJob.create to fail
        original_create = IdentifyStarsJob.create

        def _create_failure(*args, **kwargs):
            raise Exception("Database error")

        monkeypatch.setattr(create_identify_starts_job_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            create_identify_starts_job_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )
        monkeypatch.setattr(
            create_identify_starts_job_module, "upload_bytes", _upload_bytes_override
        )
        monkeypatch.setattr(IdentifyStarsJob, "create", _create_failure)

        request = self._create_valid_request()

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_create_identify_stars_job_post(request))

        assert exc_info.value.status_code == 500
        assert "Failed to create job" in exc_info.value.detail

    def test_api_create_identify_stars_job_post_image_upload_parameters(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that image is uploaded with correct parameters."""
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass  # Mock successful verification

        upload_call_params = {}

        def _upload_bytes_override(**kwargs):
            upload_call_params.update(kwargs)

        monkeypatch.setattr(create_identify_starts_job_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            create_identify_starts_job_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )
        monkeypatch.setattr(
            create_identify_starts_job_module, "upload_bytes", _upload_bytes_override
        )

        # Execute
        request = self._create_valid_request()
        image_bytes = base64.b64decode(request.image)
        result = asyncio.run(api_create_identify_stars_job_post(request))

        # Verify upload parameters
        assert upload_call_params["bucket_name"] == tos_const.IDENTIFY_STARS_BUCKET_NAME
        assert upload_call_params["content_type"] == "image/jpeg"
        assert upload_call_params["data"] == image_bytes
        assert "123/" in upload_call_params["object_name"]
        assert upload_call_params["object_name"].endswith(".jpg")
