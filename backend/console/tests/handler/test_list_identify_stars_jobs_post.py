import asyncio
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.console.handler import list_identify_stars_jobs as list_identify_stars_jobs_module
from backend.console.handler.list_identify_stars_jobs import api_list_identify_stars_jobs_post
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.console.utils import auth as auth_module
from backend.constant.sort import SORT_ORDER_ASC, SORT_ORDER_DESC
from gen.py.src.openapi_server.models.api_list_identify_stars_jobs_post_request import ApiListIdentifyStarsJobsPostRequest
from backend.constant.sort import SORT_BY_CREATE_TIME
from backend.constant.star_identify import STAR_IDENTIFY_JOB_STATUS_PENDING


class TestApiListIdentifyStarsJobsPost:
    """Test cases for api_list_identify_stars_jobs_post handler."""

    def _create_valid_request(self, user_id="123", token="valid_token", limit=None, offset=None, sort=None, order=None):
        """Helper to create a valid request."""
        return ApiListIdentifyStarsJobsPostRequest(
            user_credentials={"userID": user_id, "token": token},
            limit=limit,
            offset=offset,
            sort=sort,
            order=order
        )

    def _create_test_jobs(self, db_session: Session, user_id: int, count: int = 3):
        """Helper to create test jobs in database. Returns list of job IDs."""
        job_ids = []
        for i in range(count):
            job = IdentifyStarsJob.create(
                db=db_session,
                user_id=user_id,
                image_key=f"test_user_{user_id}/image_{i}.jpg",
                status=STAR_IDENTIFY_JOB_STATUS_PENDING
            )
            # Store ID immediately while session is active
            job_ids.append(job.id)
        return job_ids

    def test_api_list_identify_stars_jobs_post_success(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test successful retrieval of jobs list."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_access_token_override(token):
            return {"user_id": "123"}, True

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            auth_module, "verify_access_token", _verify_access_token_override
        )

        # Create test data
        job_ids = self._create_test_jobs(db_session, user_id=123, count=3)

        # Execute
        request = self._create_valid_request(user_id="123")
        result = asyncio.run(api_list_identify_stars_jobs_post(request))

        # Verify
        assert result.identify_stars_jobs_list is not None
        assert len(result.identify_stars_jobs_list) == 3

        # Verify jobs are in descending order by default
        for i in range(len(job_ids)):
            assert result.identify_stars_jobs_list[i].job_id == str(
                job_ids[-(i+1)])
            assert result.identify_stars_jobs_list[i].status == STAR_IDENTIFY_JOB_STATUS_PENDING
            assert result.identify_stars_jobs_list[i].create_time is not None
            assert result.identify_stars_jobs_list[i].update_time is not None

    def test_api_list_identify_stars_jobs_post_empty_list(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test retrieval when user has no jobs."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            list_identify_stars_jobs_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        # Execute without creating any jobs
        request = self._create_valid_request(user_id="999")
        result = asyncio.run(api_list_identify_stars_jobs_post(request))

        # Verify
        assert result.identify_stars_jobs_list is not None
        assert len(result.identify_stars_jobs_list) == 0

    def test_api_list_identify_stars_jobs_post_with_pagination(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test pagination with limit and offset."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            list_identify_stars_jobs_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        # Create 5 test jobs
        job_ids = self._create_test_jobs(db_session, user_id=123, count=5)

        # Test with limit
        request = self._create_valid_request(user_id="123", limit=2)
        result = asyncio.run(api_list_identify_stars_jobs_post(request))
        assert len(result.identify_stars_jobs_list) == 2

        # Test with limit and offset
        request = self._create_valid_request(user_id="123", limit=2, offset=2)
        result = asyncio.run(api_list_identify_stars_jobs_post(request))
        assert len(result.identify_stars_jobs_list) == 2
        # Should get the 3rd and 4th jobs (in descending order)
        assert result.identify_stars_jobs_list[0].job_id == str(job_ids[2])
        assert result.identify_stars_jobs_list[1].job_id == str(job_ids[1])

    def test_api_list_identify_stars_jobs_post_with_asc_order(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test ascending order sorting."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            list_identify_stars_jobs_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        # Create test data
        job_ids = self._create_test_jobs(db_session, user_id=123, count=3)

        # Execute with ascending order
        request = self._create_valid_request(
            user_id="123", order=SORT_ORDER_ASC)
        result = asyncio.run(api_list_identify_stars_jobs_post(request))

        # Verify jobs are in ascending order
        assert len(result.identify_stars_jobs_list) == 3
        for i in range(len(job_ids)):
            assert result.identify_stars_jobs_list[i].job_id == str(job_ids[i])

    def test_api_list_identify_stars_jobs_post_with_desc_order(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test descending order sorting (explicit)."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            list_identify_stars_jobs_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        # Create test data
        job_ids = self._create_test_jobs(db_session, user_id=123, count=3)

        # Execute with explicit descending order
        request = self._create_valid_request(
            user_id="123", order=SORT_ORDER_DESC)
        result = asyncio.run(api_list_identify_stars_jobs_post(request))

        # Verify jobs are in descending order
        assert len(result.identify_stars_jobs_list) == 3
        for i in range(len(job_ids)):
            assert result.identify_stars_jobs_list[i].job_id == str(
                job_ids[-(i+1)])

    def test_api_list_identify_stars_jobs_post_invalid_sort_field(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test request with unsupported sort field."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            list_identify_stars_jobs_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        # Execute with invalid sort field
        request = self._create_valid_request(user_id="123", sort="status")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_list_identify_stars_jobs_post(request))

        assert exc_info.value.status_code == 400

    def test_api_list_identify_stars_jobs_post_valid_sort_field(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test request with valid sort field (create_time)."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            list_identify_stars_jobs_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        # Create test data
        self._create_test_jobs(db_session, user_id=123, count=2)

        # Execute with valid sort field
        request = self._create_valid_request(
            user_id="123", sort=SORT_BY_CREATE_TIME, order=SORT_ORDER_ASC)
        result = asyncio.run(api_list_identify_stars_jobs_post(request))

        # Should succeed without error
        assert result.identify_stars_jobs_list is not None
        assert len(result.identify_stars_jobs_list) == 2

    def test_api_list_identify_stars_jobs_post_invalid_token(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test request with invalid token."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_access_token_override(token):
            return None, False

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            auth_module, "verify_access_token", _verify_access_token_override
        )

        request = self._create_valid_request(
            user_id="123", token="invalid_token")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_list_identify_stars_jobs_post(request))

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid or expired token"

    def test_api_list_identify_stars_jobs_post_user_id_mismatch(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test token belongs to different user."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_access_token_override(token):
            return {"user_id": "999"}, True  # Different user ID

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            auth_module, "verify_access_token", _verify_access_token_override
        )

        request = self._create_valid_request(user_id="123")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_list_identify_stars_jobs_post(request))

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "User ID mismatch"

    def test_api_list_identify_stars_jobs_post_database_error(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test when database query fails."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass

        # Mock list_by_user_id to fail
        def _list_by_user_id_failure(*args, **kwargs):
            raise Exception("Database connection error")

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            list_identify_stars_jobs_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )
        monkeypatch.setattr(
            IdentifyStarsJob, "list_by_user_id", _list_by_user_id_failure)

        request = self._create_valid_request(user_id="123")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_list_identify_stars_jobs_post(request))

        assert exc_info.value.status_code == 500
        assert "Failed to list jobs" in exc_info.value.detail

    def test_api_list_identify_stars_jobs_post_only_returns_users_jobs(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that users only see their own jobs."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            list_identify_stars_jobs_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        # Create jobs for two different users
        user1_job_ids = self._create_test_jobs(
            db_session, user_id=123, count=3)
        user2_job_ids = self._create_test_jobs(
            db_session, user_id=456, count=2)

        # Request jobs for user 123
        request = self._create_valid_request(user_id="123")
        result = asyncio.run(api_list_identify_stars_jobs_post(request))

        # Verify only user 123's jobs are returned
        assert len(result.identify_stars_jobs_list) == 3
        returned_job_ids = [int(job.job_id)
                            for job in result.identify_stars_jobs_list]
        for job_id in user1_job_ids:
            assert job_id in returned_job_ids
        for job_id in user2_job_ids:
            assert job_id not in returned_job_ids

    def test_api_list_identify_stars_jobs_post_default_limit(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test default limit of 20 when not specified."""
        # Setup
        def _get_db_override():
            yield db_session

        def _verify_user_id_and_token_override(token, user_id):
            pass

        monkeypatch.setattr(list_identify_stars_jobs_module,
                            "get_db", _get_db_override)
        monkeypatch.setattr(
            list_identify_stars_jobs_module, "verify_user_id_and_token", _verify_user_id_and_token_override
        )

        # Create 25 jobs (more than default limit)
        self._create_test_jobs(db_session, user_id=123, count=25)

        # Execute without specifying limit
        request = self._create_valid_request(user_id="123")
        result = asyncio.run(api_list_identify_stars_jobs_post(request))

        # Verify default limit of 20 is applied
        assert len(result.identify_stars_jobs_list) == 20
