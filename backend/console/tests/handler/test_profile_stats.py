import asyncio
import pytest
from datetime import datetime
from unittest.mock import MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

# Import the module under test and dependencies
from backend.console.handler import profile_stats as handler_module
from backend.console.handler.profile_stats import api_get_profile_stats_post
from backend.console.dal.rds.user import User as UserDAL
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob as IdentifyStarsJobDAL
from backend.console.dal.rds.user_discovered_stars import UserDiscoveredStars as UserDiscoveredStarsDAL

# OpenAPI Models
from gen.py.src.openapi_server.models.profile_stats_request import ProfileStatsRequest
from gen.py.src.openapi_server.models.user_credentials import UserCredentials

class TestApiGetProfileStatsPost:
    """Test cases for api_get_profile_stats_post handler."""

    def _create_valid_request(self, user_id="1", token="valid_token"):
        """Helper to create a valid ProfileStatsRequest."""
        # Instead of passing UserCredentials object, pass a dictionary
        return ProfileStatsRequest(
            user_credentials={
                "user_id": user_id, 
                "token": token
            }
        )

    def test_api_get_profile_stats_success(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test successful retrieval of profile stats and rank calculation."""
        user_id = 1
        
        # 1. Mock the User Object
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.username = "sasa"
        mock_user.is_deleted = False
        mock_user.created_at = datetime(2026, 3, 1) # Expected output: "Mar 2026"

        # 2. Set up Mocks for Authentication and DB
        def _get_db_override():
            yield db_session

        def _verify_auth_override(token, uid):
            pass

        monkeypatch.setattr(handler_module, "get_db", _get_db_override)
        monkeypatch.setattr(handler_module, "verify_user_id_and_token", _verify_auth_override)
        
        # Mock DAL Methods
        monkeypatch.setattr(UserDAL, "get_by_id", lambda db, uid: mock_user)
        # Mock 15 discoveries to trigger the "Explorer" rank (>= 10)
        monkeypatch.setattr(UserDiscoveredStarsDAL, "count_user_discoveries", lambda db, uid: 15)
        # Mock 5 total scans
        monkeypatch.setattr(IdentifyStarsJobDAL, "count_all_time_scans", lambda db, uid: 5)

        # 3. Execute
        request = self._create_valid_request(user_id=str(user_id))
        result = asyncio.run(api_get_profile_stats_post(request))

        # 4. Verify
        assert result.stars_discovered == 15
        assert result.total_scans == 5
        assert result.rank == "Explorer"
        assert result.join_date == "Mar 2026"

    def test_api_get_profile_stats_user_not_found(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test error when user ID does not exist in database."""
        def _get_db_override(): yield db_session
        def _verify_auth_override(token, uid): pass

        monkeypatch.setattr(handler_module, "get_db", _get_db_override)
        monkeypatch.setattr(handler_module, "verify_user_id_and_token", _verify_auth_override)
        
        # Simulate User not found
        monkeypatch.setattr(UserDAL, "get_by_id", lambda db, uid: None)

        request = self._create_valid_request(user_id="999")

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_get_profile_stats_post(request))

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"

    def test_api_get_profile_stats_rank_star_lord(
        self, db_session: Session, monkeypatch: pytest.MonkeyPatch
    ):
        """Test that rank correctly updates to Star Lord for high discovery counts."""
        user_id = 1
        mock_user = MagicMock()
        mock_user.created_at = datetime.now()
        mock_user.is_deleted = False

        def _get_db_override(): yield db_session
        def _verify_auth_override(token, uid): pass

        monkeypatch.setattr(handler_module, "get_db", _get_db_override)
        monkeypatch.setattr(handler_module, "verify_user_id_and_token", _verify_auth_override)
        monkeypatch.setattr(UserDAL, "get_by_id", lambda db, uid: mock_user)
        
        # Mock 250 discoveries to trigger "Star Lord" (>= 200)
        monkeypatch.setattr(UserDiscoveredStarsDAL, "count_user_discoveries", lambda db, uid: 250)
        monkeypatch.setattr(IdentifyStarsJobDAL, "count_all_time_scans", lambda db, uid: 100)

        request = self._create_valid_request(user_id=str(user_id))
        result = asyncio.run(api_get_profile_stats_post(request))

        assert result.rank == "Star Lord"
        assert result.stars_discovered == 250