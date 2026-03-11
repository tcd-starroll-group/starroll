import asyncio
import json
from collections import Counter
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from backend.console.handler import get_stargazing_recommendation as rec_module
from backend.console.handler.get_stargazing_recommendation import (
    _build_constellation_recommendations,
    _extract_constellations_from_result,
    _generate_tips,
    _get_moon_info,
    api_get_stargazing_recommendation_post,
    SEASONAL_CONSTELLATIONS,
    PROPER_STAR_NAMES,
)
from backend.console.dal.rds.identify_stars_job import IdentifyStarsJob
from backend.console.dal.rds.user import User
from backend.constant.star_identify import STAR_IDENTIFY_JOB_STATUS_SUCCEEDED
from gen.py.src.openapi_server.models.api_get_stargazing_recommendation_post_request import (
    ApiGetStargazingRecommendationPostRequest,
)
from gen.py.src.openapi_server.models.stargazing_recommendation_moon_phase import (
    StargazingRecommendationMoonPhase,
)
# Must use the same import path as the handler so Pydantic validates correctly
from openapi_server.models.stargazing_recommendation_best_time_slots_inner import (
    StargazingRecommendationBestTimeSlotsInner,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_request(user_id="1", token="valid_token", lat=53.35, lon=-6.26, target_date=None):
    return ApiGetStargazingRecommendationPostRequest(
        userCredentials={"userID": user_id, "token": token},
        gps={"latitude": lat, "longitude": lon},
        targetDate=target_date,
    )


def _make_slot(hour=22, sky="clear", score=80.0) -> StargazingRecommendationBestTimeSlotsInner:
    dt = datetime(2026, 3, 9, hour, 0)
    return StargazingRecommendationBestTimeSlotsInner(
        start_time=dt,
        end_time=dt + timedelta(hours=2),
        score=score,
        sky_condition=sky,
    )


def _make_job_with_result(hour=22, names=None, status=None):
    """Create a mock identify-stars job with the given result star names."""
    names = names or ["alphOri", "betaTau"]
    result_data = json.dumps({
        "stars": [{"names": names, "pixelx": 0.0, "pixely": 0.0, "vmag": 1.0, "type": "star"}],
        "calibration": {"ra": 0, "dec": 0, "parity": 1, "orientation": 0, "pixscale": 1, "radius": 1},
    })
    job = MagicMock()
    job.result = result_data
    job.created_at = datetime(2026, 3, 9, hour, 0)
    job.status = status if status is not None else STAR_IDENTIFY_JOB_STATUS_SUCCEEDED
    return job


def _setup_common_mocks(monkeypatch, db_session, jobs=None, slots=None):
    """Apply the most common mock setup: pass auth, inject db, stub weather."""
    def _get_db_override():
        yield db_session

    monkeypatch.setattr(rec_module, "get_db", _get_db_override)
    monkeypatch.setattr(rec_module, "verify_user_id_and_token", lambda token, uid: None)
    monkeypatch.setattr(
        IdentifyStarsJob, "list_by_user_id",
        MagicMock(return_value=jobs if jobs is not None else []),
    )

    default_slots = [_make_slot(22, "clear", 85.0)]
    monkeypatch.setattr(
        rec_module, "_fetch_top_slots",
        AsyncMock(return_value=slots if slots is not None else default_slots),
    )


# ===========================================================================
# Unit tests — _extract_constellations_from_result
# ===========================================================================

class TestExtractConstellations:
    def test_extracts_known_iau_suffix(self):
        result = {
            "stars": [
                {"names": ["alphOri", "betaTau"]},
                {"names": ["108Vir"]},
            ]
        }
        consts = _extract_constellations_from_result(result)
        assert "Orion" in consts
        assert "Taurus" in consts
        assert "Virgo" in consts

    def test_proper_name_sirius(self):
        result = {"stars": [{"names": ["Sirius"]}]}
        assert "Canis Major" in _extract_constellations_from_result(result)

    def test_proper_name_case_insensitive(self):
        result = {"stars": [{"names": ["sirius"]}]}
        assert "Canis Major" in _extract_constellations_from_result(result)

    def test_proper_name_betelgeuse(self):
        result = {"stars": [{"names": ["Betelgeuse"]}]}
        assert "Orion" in _extract_constellations_from_result(result)

    def test_sliding_window_finds_embedded_abbreviation(self):
        # "alphaCMa" — IAU code "CMa" sits at index 5, not the last 3 chars
        result = {"stars": [{"names": ["alphaCMa"]}]}
        assert "Canis Major" in _extract_constellations_from_result(result)

    def test_empty_result_returns_empty_list(self):
        assert _extract_constellations_from_result({}) == []

    def test_no_matching_abbreviations(self):
        result = {"stars": [{"names": ["XYZ", "AB"]}]}
        assert _extract_constellations_from_result(result) == []

    def test_duplicate_stars_deduplicated(self):
        # Two Orion stars → still one "Orion" entry
        result = {"stars": [{"names": ["alphOri"]}, {"names": ["betOri"]}]}
        consts = _extract_constellations_from_result(result)
        assert consts.count("Orion") == 1

    def test_empty_names_list(self):
        result = {"stars": [{"names": []}]}
        assert _extract_constellations_from_result(result) == []

    def test_proper_star_names_dict_is_populated(self):
        assert "sirius" in PROPER_STAR_NAMES
        assert "vega" in PROPER_STAR_NAMES
        assert "polaris" in PROPER_STAR_NAMES


# ===========================================================================
# Unit tests — _get_moon_info
# ===========================================================================

class TestGetMoonInfo:
    def test_new_moon_known_date(self):
        info = _get_moon_info(date(2000, 1, 6))
        assert info.phase == "New Moon"
        assert info.illumination < 0.05

    def test_full_moon_approx(self):
        info = _get_moon_info(date(2000, 1, 20))
        assert info.phase in ("Full Moon", "Waxing Gibbous")
        assert info.illumination > 0.8

    def test_illumination_always_in_valid_range(self):
        for day in range(1, 30):
            info = _get_moon_info(date(2026, 3, day))
            assert 0.0 <= info.illumination <= 1.0, f"Day {day}: {info.illumination}"

    def test_returns_moon_phase_model(self):
        info = _get_moon_info(date(2026, 3, 9))
        assert info.phase in (
            "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
            "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent",
        )
        assert isinstance(info.illumination, float)
        assert 0.0 <= info.illumination <= 1.0


# ===========================================================================
# Unit tests — _build_constellation_recommendations
# ===========================================================================

class TestBuildConstellationRecommendations:
    def test_user_history_appears_first(self):
        counter = Counter({"Orion": 10, "Leo": 5})
        recs = _build_constellation_recommendations(counter, date(2026, 1, 15))
        assert recs[0].name == "Orion"
        assert recs[1].name == "Leo"

    def test_cold_start_uses_seasonal_constellations(self):
        recs = _build_constellation_recommendations(Counter(), date(2026, 12, 15))
        names = [r.name for r in recs]
        seasonal_names = [name for name, _ in SEASONAL_CONSTELLATIONS[12]]
        assert any(n in seasonal_names for n in names)

    def test_user_reason_includes_observation_count(self):
        counter = Counter({"Gemini": 4})
        recs = _build_constellation_recommendations(counter, date(2026, 2, 10))
        gemini_rec = next(r for r in recs if r.name == "Gemini")
        assert "4 times" in gemini_rec.reason

    def test_singular_observation_reason(self):
        counter = Counter({"Leo": 1})
        recs = _build_constellation_recommendations(counter, date(2026, 4, 10))
        leo_rec = next(r for r in recs if r.name == "Leo")
        assert "1 time" in leo_rec.reason and "times" not in leo_rec.reason

    def test_no_duplicates_in_result(self):
        counter = Counter({"Orion": 5})
        recs = _build_constellation_recommendations(counter, date(2026, 1, 15))
        names = [r.name for r in recs]
        assert len(names) == len(set(names))

    def test_max_five_results(self):
        counter = Counter({"Orion": 5, "Leo": 4, "Virgo": 3, "Cygnus": 2, "Lyra": 1})
        recs = _build_constellation_recommendations(counter, date(2026, 7, 15))
        assert len(recs) <= 5


# ===========================================================================
# Unit tests — _generate_tips
# ===========================================================================

class TestGenerateTips:
    def _moon(self, illumination: float, phase: str) -> StargazingRecommendationMoonPhase:
        return StargazingRecommendationMoonPhase(illumination=illumination, phase=phase)

    def test_new_moon_tip_mentions_ideal_darkness(self):
        tips = _generate_tips(self._moon(0.02, "New Moon"), [], Counter(), date(2026, 3, 9))
        assert any("New Moon" in t or "ideal darkness" in t for t in tips)

    def test_full_moon_tip_warns_about_brightness(self):
        tips = _generate_tips(self._moon(0.95, "Full Moon"), [], Counter(), date(2026, 3, 9))
        assert any("Full Moon" in t or "lunar" in t.lower() for t in tips)

    def test_clear_sky_slot_tip(self):
        slots = [_make_slot(22, "clear")]
        tips = _generate_tips(self._moon(0.3, "Waxing Crescent"), slots, Counter(), date(2026, 3, 9))
        assert any("clear" in t.lower() or "Clear" in t for t in tips)

    def test_cloudy_sky_tip(self):
        slots = [_make_slot(22, "cloudy", 20.0)]
        tips = _generate_tips(self._moon(0.5, "First Quarter"), slots, Counter(), date(2026, 3, 9))
        assert any("cloud" in t.lower() or "tomorrow" in t.lower() for t in tips)

    def test_user_habit_tip_shows_hour(self):
        hour_counter = Counter({23: 10, 0: 5})
        tips = _generate_tips(self._moon(0.5, "First Quarter"), [], hour_counter, date(2026, 3, 9))
        assert any("23:00" in t for t in tips)

    def test_seasonal_tip_included(self):
        tips = _generate_tips(self._moon(0.5, "First Quarter"), [], Counter(), date(2026, 12, 15))
        assert any("December" in t or "Orion" in t or "Taurus" in t for t in tips)

    def test_returns_list_of_strings(self):
        tips = _generate_tips(self._moon(0.3, "Waxing Crescent"), [], Counter(), date(2026, 3, 9))
        assert isinstance(tips, list)
        assert all(isinstance(t, str) for t in tips)

    def test_tip_uses_highest_score_slot_not_earliest(self):
        """The sky tip must reference the best-scored slot, not the first chronologically."""
        early_bad = _make_slot(hour=21, sky="cloudy", score=15.0)
        late_good = _make_slot(hour=23, sky="clear", score=90.0)
        # early_bad is chronologically first but worst in score
        tips = _generate_tips(
            self._moon(0.3, "Waxing Crescent"), [early_bad, late_good], Counter(), date(2026, 3, 9)
        )
        # Tip should reflect clear sky (from the highest-scored slot)
        assert any("clear" in t.lower() or "Clear" in t for t in tips)


# ===========================================================================
# Integration tests — api_get_stargazing_recommendation_post
# ===========================================================================

class TestApiGetStargazingRecommendationPost:

    def test_success_cold_start(self, db_session, monkeypatch):
        """New user with no history still gets a valid recommendation."""
        _setup_common_mocks(monkeypatch, db_session)
        result = asyncio.run(api_get_stargazing_recommendation_post(_make_request()))

        assert result.moon_phase is not None
        assert result.best_time_slots is not None
        assert len(result.best_time_slots) > 0
        assert result.recommended_constellations is not None
        assert len(result.recommended_constellations) > 0
        assert result.tips is not None
        assert len(result.tips) > 0

    def test_success_with_history_personalises_constellations(self, db_session, monkeypatch):
        """User with Orion SUCCEEDED jobs gets Orion in their recommendations."""
        jobs = [_make_job_with_result(hour=22, names=["alphOri"]) for _ in range(5)]
        _setup_common_mocks(monkeypatch, db_session, jobs=jobs)

        result = asyncio.run(api_get_stargazing_recommendation_post(_make_request()))
        names = [r.name for r in result.recommended_constellations]
        assert "Orion" in names

    def test_only_succeeded_jobs_used_in_fallback(self, db_session, monkeypatch):
        """Failed jobs must be ignored; only SUCCEEDED jobs contribute to preferences."""
        succeeded = _make_job_with_result(names=["alphOri"])
        failed = _make_job_with_result(names=["108Leo"], status="Failed")

        _setup_common_mocks(monkeypatch, db_session, jobs=[succeeded, failed])

        result = asyncio.run(api_get_stargazing_recommendation_post(_make_request()))
        names = [r.name for r in result.recommended_constellations]
        # Orion from succeeded job must appear; Leo from failed job must NOT
        assert "Orion" in names
        assert "Leo" not in names

    def test_profile_cache_used_when_present(self, db_session, monkeypatch):
        """When user has a stargazing_profile, job history must NOT be rescanned."""
        user = User.create(db_session, "cache_user", "hash", "cache@test.com")
        User.update_profile_by_id(db_session, user.id, {
            "stargazing_profile": {
                "preferred_constellations": ["Lyra", "Cygnus"],
                "preferred_hours": [23, 0],
                "observation_count": 10,
                "last_updated": date.today().isoformat(),
            }
        })

        def _get_db_override():
            yield db_session

        monkeypatch.setattr(rec_module, "get_db", _get_db_override)
        monkeypatch.setattr(rec_module, "verify_user_id_and_token", lambda t, u: None)
        job_scanner = MagicMock()
        monkeypatch.setattr(IdentifyStarsJob, "list_by_user_id", job_scanner)
        monkeypatch.setattr(rec_module, "_fetch_top_slots", AsyncMock(return_value=[_make_slot()]))

        result = asyncio.run(api_get_stargazing_recommendation_post(
            _make_request(user_id=str(user.id))
        ))

        # Job scanner must NOT have been called (profile was loaded from cache)
        job_scanner.assert_not_called()

        names = [r.name for r in result.recommended_constellations]
        assert "Lyra" in names or "Cygnus" in names

    def test_result_has_all_required_fields(self, db_session, monkeypatch):
        _setup_common_mocks(monkeypatch, db_session)
        result = asyncio.run(api_get_stargazing_recommendation_post(
            _make_request(target_date=date(2026, 3, 10))
        ))
        assert result.best_time_slots is not None
        assert result.recommended_constellations is not None
        assert result.moon_phase is not None
        assert result.moon_phase.illumination is not None
        assert result.moon_phase.phase is not None
        assert result.tips is not None

    def test_slots_returned_in_chronological_order(self, db_session, monkeypatch):
        """Best time slots must be sorted by startTime ascending."""
        out_of_order_slots = [
            _make_slot(hour=2, sky="clear", score=70.0),
            _make_slot(hour=22, sky="clear", score=90.0),
        ]
        _setup_common_mocks(monkeypatch, db_session, slots=out_of_order_slots)

        result = asyncio.run(api_get_stargazing_recommendation_post(_make_request()))
        start_times = [s.start_time for s in result.best_time_slots]
        assert start_times == sorted(start_times)

    def test_missing_gps_raises_400(self, db_session, monkeypatch):
        req = ApiGetStargazingRecommendationPostRequest(
            userCredentials={"userID": "1", "token": "tok"},
            gps=None,
        )
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_get_stargazing_recommendation_post(req))
        assert exc_info.value.status_code == 400

    def test_missing_credentials_raises_400(self, db_session, monkeypatch):
        req = ApiGetStargazingRecommendationPostRequest(
            userCredentials=None,
            gps={"latitude": 53.35, "longitude": -6.26},
        )
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_get_stargazing_recommendation_post(req))
        assert exc_info.value.status_code == 400

    def test_invalid_token_raises_401(self, db_session, monkeypatch):
        def _raise_401(token, uid):
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        monkeypatch.setattr(rec_module, "verify_user_id_and_token", _raise_401)

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_get_stargazing_recommendation_post(_make_request(token="bad")))
        assert exc_info.value.status_code == 401

    def test_user_id_mismatch_raises_403(self, db_session, monkeypatch):
        def _raise_403(token, uid):
            raise HTTPException(status_code=403, detail="User ID mismatch")

        monkeypatch.setattr(rec_module, "verify_user_id_and_token", _raise_403)

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_get_stargazing_recommendation_post(_make_request()))
        assert exc_info.value.status_code == 403

    def test_weather_api_failure_raises_502(self, db_session, monkeypatch):
        def _get_db_override():
            yield db_session

        monkeypatch.setattr(rec_module, "get_db", _get_db_override)
        monkeypatch.setattr(rec_module, "verify_user_id_and_token", lambda t, u: None)
        monkeypatch.setattr(IdentifyStarsJob, "list_by_user_id", MagicMock(return_value=[]))

        async def _fail(*args, **kwargs):
            raise HTTPException(status_code=502, detail="Failed to fetch weather data from Open-Meteo")

        monkeypatch.setattr(rec_module, "_fetch_top_slots", _fail)

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_get_stargazing_recommendation_post(_make_request()))
        assert exc_info.value.status_code == 502

    def test_db_error_raises_500(self, db_session, monkeypatch):
        def _get_db_override():
            yield db_session

        monkeypatch.setattr(rec_module, "get_db", _get_db_override)
        monkeypatch.setattr(rec_module, "verify_user_id_and_token", lambda t, u: None)
        monkeypatch.setattr(
            IdentifyStarsJob, "list_by_user_id",
            MagicMock(side_effect=Exception("DB connection lost")),
        )

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_get_stargazing_recommendation_post(_make_request()))
        assert exc_info.value.status_code == 500

    def test_bad_job_result_json_is_skipped(self, db_session, monkeypatch):
        """Jobs with unparseable results are skipped; handler still succeeds."""
        bad_job = MagicMock()
        bad_job.result = "NOT_VALID_JSON"
        bad_job.created_at = datetime(2026, 3, 9, 22, 0)
        bad_job.status = STAR_IDENTIFY_JOB_STATUS_SUCCEEDED

        _setup_common_mocks(monkeypatch, db_session, jobs=[bad_job])

        result = asyncio.run(api_get_stargazing_recommendation_post(_make_request()))
        assert result is not None


# ===========================================================================
# Integration tests — _update_one_user
# ===========================================================================

class TestUpdateOneUser:

    def test_writes_stargazing_profile_to_user(self, db_session, monkeypatch):
        from backend.cronjob.update_user_stargazing_profile import _update_one_user

        user = User.create(db_session, "tester_one", "hash", "one@test.com")
        jobs = [_make_job_with_result(hour=(22 + i) % 24) for i in range(6)]
        monkeypatch.setattr(IdentifyStarsJob, "list_by_user_id", MagicMock(return_value=jobs))

        _update_one_user(db_session, user.id)

        updated = User.get_by_id(db_session, user.id)
        sg = updated.profile["stargazing_profile"]
        assert sg["observation_count"] == 6
        assert sg["last_updated"] == date.today().isoformat()
        assert isinstance(sg["preferred_constellations"], list)
        assert isinstance(sg["preferred_hours"], list)

    def test_constellations_extracted_from_results(self, db_session, monkeypatch):
        from backend.cronjob.update_user_stargazing_profile import _update_one_user

        user = User.create(db_session, "tester_two", "hash", "two@test.com")
        jobs = [_make_job_with_result(names=["alphOri"]) for _ in range(4)]
        monkeypatch.setattr(IdentifyStarsJob, "list_by_user_id", MagicMock(return_value=jobs))

        _update_one_user(db_session, user.id)

        sg = User.get_by_id(db_session, user.id).profile["stargazing_profile"]
        assert "Orion" in sg["preferred_constellations"]

    def test_non_succeeded_jobs_not_counted(self, db_session, monkeypatch):
        """Only SUCCEEDED jobs must appear in the profile."""
        from backend.cronjob.update_user_stargazing_profile import _update_one_user

        user = User.create(db_session, "tester_status", "hash", "status@test.com")
        succeeded = _make_job_with_result(names=["alphOri"])
        failed = _make_job_with_result(names=["108Leo"], status="Failed")
        pending = _make_job_with_result(names=["betaTau"], status="Pending")

        monkeypatch.setattr(
            IdentifyStarsJob, "list_by_user_id",
            MagicMock(return_value=[succeeded, failed, pending]),
        )

        _update_one_user(db_session, user.id)

        sg = User.get_by_id(db_session, user.id).profile["stargazing_profile"]
        assert sg["observation_count"] == 1
        assert "Orion" in sg["preferred_constellations"]
        assert "Leo" not in sg["preferred_constellations"]
        assert "Taurus" not in sg["preferred_constellations"]

    def test_preserves_existing_profile_fields(self, db_session, monkeypatch):
        from backend.cronjob.update_user_stargazing_profile import _update_one_user

        user = User.create(db_session, "tester_three", "hash", "three@test.com")
        User.update_profile_by_id(db_session, user.id, {"bio": "Night sky lover"})
        monkeypatch.setattr(IdentifyStarsJob, "list_by_user_id", MagicMock(return_value=[]))

        _update_one_user(db_session, user.id)

        updated = User.get_by_id(db_session, user.id)
        assert updated.profile["bio"] == "Night sky lover"
        assert "stargazing_profile" in updated.profile

    def test_skips_nonexistent_user(self, db_session, monkeypatch):
        from backend.cronjob.update_user_stargazing_profile import _update_one_user

        monkeypatch.setattr(IdentifyStarsJob, "list_by_user_id", MagicMock(return_value=[]))
        _update_one_user(db_session, user_id=99999)

    def test_bad_result_json_skipped_gracefully(self, db_session, monkeypatch):
        from backend.cronjob.update_user_stargazing_profile import _update_one_user

        user = User.create(db_session, "tester_four", "hash", "four@test.com")
        bad_job = MagicMock()
        bad_job.result = "INVALID_JSON"
        bad_job.created_at = datetime(2026, 3, 9, 22, 0)
        bad_job.status = STAR_IDENTIFY_JOB_STATUS_SUCCEEDED

        monkeypatch.setattr(IdentifyStarsJob, "list_by_user_id", MagicMock(return_value=[bad_job]))

        _update_one_user(db_session, user.id)

        sg = User.get_by_id(db_session, user.id).profile["stargazing_profile"]
        assert sg["observation_count"] == 1
        assert sg["preferred_constellations"] == []

    def test_preferred_hours_includes_most_frequent(self, db_session, monkeypatch):
        from backend.cronjob.update_user_stargazing_profile import _update_one_user

        user = User.create(db_session, "tester_five", "hash", "five@test.com")
        jobs = (
            [_make_job_with_result(hour=23)] * 5 +
            [_make_job_with_result(hour=22)] * 2 +
            [_make_job_with_result(hour=0)] * 1
        )
        monkeypatch.setattr(IdentifyStarsJob, "list_by_user_id", MagicMock(return_value=jobs))

        _update_one_user(db_session, user.id)

        sg = User.get_by_id(db_session, user.id).profile["stargazing_profile"]
        assert 23 in sg["preferred_hours"]
