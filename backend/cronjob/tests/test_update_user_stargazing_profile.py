from unittest.mock import MagicMock, call

import pytest

from backend.cronjob.update_user_stargazing_profile import update_user_stargazing_profile_handler
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
import backend.cronjob.update_user_stargazing_profile as profile_module


class TestUpdateUserStargazingProfileHandler:

    def test_no_active_users_runs_silently(self, monkeypatch):
        """Handler completes without error when there are no active users."""
        mock_db = MagicMock()
        monkeypatch.setattr(profile_module, "get_db", lambda: iter([mock_db]))
        monkeypatch.setattr(
            IdentifyStarsJob, "list_recent_user_ids", MagicMock(return_value=[])
        )
        update_user_stargazing_profile_handler()  # Must not raise

    def test_calls_update_for_each_active_user(self, monkeypatch):
        """_update_one_user is called once per active user."""
        mock_db = MagicMock()
        monkeypatch.setattr(profile_module, "get_db", lambda: iter([mock_db]))
        monkeypatch.setattr(
            IdentifyStarsJob, "list_recent_user_ids", MagicMock(return_value=[10, 20, 30])
        )
        mock_update = MagicMock()
        monkeypatch.setattr(profile_module, "_update_one_user", mock_update)

        update_user_stargazing_profile_handler()

        assert mock_update.call_count == 3
        mock_update.assert_any_call(mock_db, 10)
        mock_update.assert_any_call(mock_db, 20)
        mock_update.assert_any_call(mock_db, 30)

    def test_continues_after_one_user_fails(self, monkeypatch):
        """If one user update raises, the handler still processes the rest."""
        mock_db = MagicMock()
        monkeypatch.setattr(profile_module, "get_db", lambda: iter([mock_db]))
        monkeypatch.setattr(
            IdentifyStarsJob, "list_recent_user_ids", MagicMock(return_value=[101, 102, 103])
        )
        processed = []

        def _flaky_update(db, user_id):
            processed.append(user_id)
            if user_id == 102:
                raise Exception("Simulated failure for user 102")

        monkeypatch.setattr(profile_module, "_update_one_user", _flaky_update)

        update_user_stargazing_profile_handler()  # Must not raise

        assert 101 in processed
        assert 102 in processed
        assert 103 in processed

    def test_db_session_is_always_closed(self, monkeypatch):
        """The DB session close() must be called even if something goes wrong."""
        mock_db = MagicMock()
        monkeypatch.setattr(profile_module, "get_db", lambda: iter([mock_db]))
        monkeypatch.setattr(
            IdentifyStarsJob, "list_recent_user_ids", MagicMock(side_effect=Exception("DB exploded"))
        )

        with pytest.raises(Exception, match="DB exploded"):
            update_user_stargazing_profile_handler()

        mock_db.close.assert_called_once()
