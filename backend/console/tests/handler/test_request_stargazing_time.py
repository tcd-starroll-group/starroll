import asyncio
import json
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import HTTPException

from backend.console.handler import request_stargazing_time as rst_module
from backend.console.handler.request_stargazing_time import (
    _calculate_moon_illumination,
    _get_cache_key,
    _get_sky_condition,
    _is_night_hour,
    _score_hour,
    api_request_stargazing_time_post,
)
from gen.py.src.openapi_server.models.api_request_stargazing_time_post_request import (
    ApiRequestStargazingTimePostRequest,
)

# ---------------------------------------------------------------------------
# Shared fixture: two days of hourly weather data (clear night)
# ---------------------------------------------------------------------------

_CLEAR_METEO_RESPONSE = {
    "hourly": {
        "time": (
            [f"2026-03-09T{h:02d}:00" for h in range(24)] +
            [f"2026-03-10T{h:02d}:00" for h in range(24)]
        ),
        "cloud_cover": [5] * 48,
        "precipitation_probability": [0] * 48,
    }
}


def _make_request(lat=53.35, lon=-6.26, target_date=None):
    return ApiRequestStargazingTimePostRequest(
        gps={"latitude": lat, "longitude": lon},
        targetDate=target_date,
    )


def _mock_http_success(monkeypatch, payload=None):
    """Replace httpx.AsyncClient so it returns a successful Open-Meteo response."""
    payload = payload or _CLEAR_METEO_RESPONSE
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = payload

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.get = AsyncMock(return_value=mock_resp)

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: mock_client)
    return mock_client


# ===========================================================================
# Unit tests — _calculate_moon_illumination
# ===========================================================================

class TestCalculateMoonIllumination:
    def test_new_moon_epoch(self):
        # Jan 6 2000 is the known new moon used as epoch
        val = _calculate_moon_illumination(date(2000, 1, 6))
        assert val < 0.05

    def test_full_moon_approx(self):
        # ~14 days later
        val = _calculate_moon_illumination(date(2000, 1, 20))
        assert val > 0.85

    def test_output_always_in_0_1(self):
        for day in range(1, 30):
            val = _calculate_moon_illumination(date(2026, 3, day))
            assert 0.0 <= val <= 1.0, f"day={day}: {val}"


# ===========================================================================
# Unit tests — _score_hour
# ===========================================================================

class TestScoreHour:
    def test_perfect_conditions(self):
        assert _score_hour(0, 0, 0.0) == 100.0

    def test_worst_conditions(self):
        assert _score_hour(100, 100, 1.0) == 0.0

    def test_cloud_has_dominant_weight(self):
        # 100% cloud vs 100% moon — full cloud should be worse
        score_all_cloud = _score_hour(100, 0, 0.0)
        score_full_moon = _score_hour(0, 0, 1.0)
        assert score_all_cloud < score_full_moon

    def test_score_always_in_range(self):
        for cloud in (0, 50, 100):
            for precip in (0, 50, 100):
                for moon in (0.0, 0.5, 1.0):
                    s = _score_hour(cloud, precip, moon)
                    assert 0.0 <= s <= 100.0, f"cloud={cloud} precip={precip} moon={moon}: {s}"


# ===========================================================================
# Unit tests — _is_night_hour
# ===========================================================================

class TestIsNightHour:
    def test_evening_hours_are_night(self):
        assert _is_night_hour(20) is True
        assert _is_night_hour(23) is True

    def test_midnight_and_early_morning_are_night(self):
        assert _is_night_hour(0) is True
        assert _is_night_hour(3) is True
        assert _is_night_hour(5) is True

    def test_daytime_hours_are_not_night(self):
        assert _is_night_hour(6) is False
        assert _is_night_hour(12) is False
        assert _is_night_hour(18) is False
        assert _is_night_hour(19) is False


# ===========================================================================
# Unit tests — _get_sky_condition
# ===========================================================================

class TestGetSkyCondition:
    def test_below_25_is_clear(self):
        assert _get_sky_condition(0) == "clear"
        assert _get_sky_condition(24) == "clear"

    def test_boundary_25_is_partly_cloudy(self):
        assert _get_sky_condition(25) == "partly-cloudy"

    def test_below_60_is_partly_cloudy(self):
        assert _get_sky_condition(59) == "partly-cloudy"

    def test_at_and_above_60_is_cloudy(self):
        assert _get_sky_condition(60) == "cloudy"
        assert _get_sky_condition(100) == "cloudy"


# ===========================================================================
# Unit tests — _get_cache_key
# ===========================================================================

class TestGetCacheKey:
    def test_key_contains_date(self):
        key = _get_cache_key(53.35, -6.26, date(2026, 3, 9))
        assert "2026-03-09" in key

    def test_coords_rounded_to_2_decimal_places(self):
        # Both slightly different coords should map to same key
        key1 = _get_cache_key(53.3498, -6.2603, date(2026, 3, 9))
        key2 = _get_cache_key(53.3501, -6.2598, date(2026, 3, 9))
        assert key1 == key2

    def test_different_coords_yield_different_keys(self):
        key1 = _get_cache_key(53.35, -6.26, date(2026, 3, 9))
        key2 = _get_cache_key(48.86, 2.35, date(2026, 3, 9))
        assert key1 != key2

    def test_different_dates_yield_different_keys(self):
        key1 = _get_cache_key(53.35, -6.26, date(2026, 3, 9))
        key2 = _get_cache_key(53.35, -6.26, date(2026, 3, 10))
        assert key1 != key2


# ===========================================================================
# Integration tests — api_request_stargazing_time_post
# ===========================================================================

class TestApiRequestStargazingTimePost:

    def test_success_returns_valid_response(self, monkeypatch):
        monkeypatch.setattr(rst_module, "_get_redis", lambda: None)
        _mock_http_success(monkeypatch)

        result = asyncio.run(api_request_stargazing_time_post(_make_request()))

        assert result is not None
        assert result.optimal_time_range is not None
        assert result.optimal_time_range.start_time < result.optimal_time_range.end_time
        assert result.sky_condition in ("clear", "partly-cloudy", "cloudy")

    def test_defaults_to_today_when_no_date(self, monkeypatch):
        monkeypatch.setattr(rst_module, "_get_redis", lambda: None)
        _mock_http_success(monkeypatch)

        req = ApiRequestStargazingTimePostRequest(gps={"latitude": 53.35, "longitude": -6.26})
        result = asyncio.run(api_request_stargazing_time_post(req))
        assert result is not None

    def test_missing_gps_raises_400(self, monkeypatch):
        req = ApiRequestStargazingTimePostRequest(gps=None)
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_request_stargazing_time_post(req))
        assert exc_info.value.status_code == 400

    def test_weather_api_failure_raises_502(self, monkeypatch):
        monkeypatch.setattr(rst_module, "_get_redis", lambda: None)

        mock_resp = MagicMock()
        mock_resp.status_code = 503

        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_resp)
        monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: mock_client)

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(api_request_stargazing_time_post(_make_request()))
        assert exc_info.value.status_code == 502

    def test_cache_hit_returns_result_without_calling_api(self, monkeypatch):
        """When Redis has a cached result, Open-Meteo must NOT be called."""
        cached_payload = json.dumps({
            "skyCondition": "clear",
            "startTime": "2026-03-09T23:00:00",
            "endTime": "2026-03-10T01:00:00",
        })
        mock_redis = MagicMock()
        mock_redis.get.return_value = cached_payload
        monkeypatch.setattr(rst_module, "_get_redis", lambda: mock_redis)

        http_call_count = {"n": 0}

        class _NeverCalledClient:
            async def __aenter__(self):
                http_call_count["n"] += 1
                return self
            async def __aexit__(self, *a):
                pass
            async def get(self, *a, **kw):
                return MagicMock(status_code=200, json=lambda: {})

        monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: _NeverCalledClient())

        result = asyncio.run(api_request_stargazing_time_post(_make_request()))

        assert http_call_count["n"] == 0
        assert result.sky_condition == "clear"

    def test_cache_miss_writes_result_to_redis(self, monkeypatch):
        """On a cache miss the handler must write the result back to Redis."""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None  # Cache miss
        monkeypatch.setattr(rst_module, "_get_redis", lambda: mock_redis)
        _mock_http_success(monkeypatch)

        asyncio.run(api_request_stargazing_time_post(_make_request()))

        mock_redis.set.assert_called_once()

    def test_redis_failure_falls_back_to_api(self, monkeypatch):
        """If Redis is broken, the handler still works by calling Open-Meteo."""
        mock_redis = MagicMock()
        mock_redis.get.side_effect = Exception("Redis down")
        monkeypatch.setattr(rst_module, "_get_redis", lambda: mock_redis)
        _mock_http_success(monkeypatch)

        result = asyncio.run(api_request_stargazing_time_post(_make_request()))
        assert result is not None

    def test_all_cloudy_night_returns_cloudy_condition(self, monkeypatch):
        monkeypatch.setattr(rst_module, "_get_redis", lambda: None)
        _mock_http_success(monkeypatch, payload={
            "hourly": {
                "time": (
                    [f"2026-03-09T{h:02d}:00" for h in range(24)] +
                    [f"2026-03-10T{h:02d}:00" for h in range(24)]
                ),
                "cloud_cover": [95] * 48,
                "precipitation_probability": [80] * 48,
            }
        })

        result = asyncio.run(api_request_stargazing_time_post(_make_request()))
        assert result.sky_condition == "cloudy"
