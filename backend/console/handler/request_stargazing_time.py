import json
import logging
import math
import httpx
from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import HTTPException

from openapi_server.models.api_request_stargazing_time_post_request import ApiRequestStargazingTimePostRequest
from openapi_server.models.api_request_stargazing_time_post200_response import ApiRequestStargazingTimePost200Response
from openapi_server.models.api_request_stargazing_time_post200_response_optimal_time_range import ApiRequestStargazingTimePost200ResponseOptimalTimeRange
from backend.console.dal.cache.client import RedisClient
from backend.config.settings import Settings

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Cache TTL: 3 hours — weather data changes slowly
CACHE_TTL_SECONDS = 3 * 60 * 60

# Nighttime window: 20:00 to 05:00 (inclusive)
NIGHT_HOURS_START = 20
NIGHT_HOURS_END = 5

# Scoring weights
WEIGHT_CLOUD = 0.5
WEIGHT_PRECIP = 0.3
WEIGHT_MOON = 0.2

# Sky condition thresholds (average cloud cover %)
CLEAR_THRESHOLD = 25
PARTLY_CLOUDY_THRESHOLD = 60


def _calculate_moon_illumination(target_date: date) -> float:
    """
    Returns moon illumination fraction (0.0 = new moon, 1.0 = full moon).
    Uses a known new moon epoch and the average lunar cycle length.
    """
    known_new_moon = datetime(2000, 1, 6, 18, 14)
    lunar_cycle_days = 29.53058867

    dt = datetime(target_date.year, target_date.month, target_date.day)
    days_since = (dt - known_new_moon).total_seconds() / 86400
    cycle_position = (days_since % lunar_cycle_days) / lunar_cycle_days

    illumination = (1 - math.cos(2 * math.pi * cycle_position)) / 2
    return illumination


def _score_hour(cloud_cover: float, precipitation_prob: float, moon_illumination: float) -> float:
    """
    Scores a single hour for stargazing quality on a scale of 0.0 to 100.0.
    Higher score means better conditions.
    """
    cloud_score = (100 - cloud_cover) / 100
    precip_score = (100 - precipitation_prob) / 100
    moon_score = 1.0 - moon_illumination

    return round(
        (cloud_score * WEIGHT_CLOUD + precip_score * WEIGHT_PRECIP + moon_score * WEIGHT_MOON) * 100,
        1,
    )


def _is_night_hour(hour: int) -> bool:
    return hour >= NIGHT_HOURS_START or hour <= NIGHT_HOURS_END


def _get_sky_condition(avg_cloud_cover: float) -> str:
    if avg_cloud_cover < CLEAR_THRESHOLD:
        return "clear"
    if avg_cloud_cover < PARTLY_CLOUDY_THRESHOLD:
        return "partly-cloudy"
    return "cloudy"


def _get_cache_key(lat: float, lon: float, target_date: date) -> str:
    # Round to 2 decimal places (~1.1 km precision) to increase cache hit rate
    return f"stargazing:{round(lat, 2)}:{round(lon, 2)}:{target_date.isoformat()}"


def _get_redis() -> Optional[RedisClient]:
    try:
        return RedisClient.get_instance(Settings())
    except Exception as e:
        logger.warning(f"Redis unavailable, cache disabled: {e}")
        return None


def _build_response(
    best_start: datetime, sky_condition: str
) -> ApiRequestStargazingTimePost200Response:
    return ApiRequestStargazingTimePost200Response(
        optimal_time_range=ApiRequestStargazingTimePost200ResponseOptimalTimeRange(
            start_time=best_start,
            end_time=best_start + timedelta(hours=2),
        ),
        sky_condition=sky_condition,
    )


async def fetch_and_score(
    lat: float, lon: float, target_date: date
) -> ApiRequestStargazingTimePost200Response:
    """Call Open-Meteo, score nighttime hours, return the best stargazing window."""
    end_date = target_date + timedelta(days=1)
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "cloud_cover,precipitation_probability",
        "timezone": "auto",
        "start_date": target_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(OPEN_METEO_URL, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch weather data from Open-Meteo")

    data = response.json()
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    cloud_covers = hourly.get("cloud_cover", [])
    precip_probs = hourly.get("precipitation_probability", [])

    moon_illumination = _calculate_moon_illumination(target_date)

    night_slots = []
    for i, t in enumerate(times):
        dt = datetime.fromisoformat(t)
        if _is_night_hour(dt.hour):
            cloud = cloud_covers[i] if i < len(cloud_covers) else 100.0
            precip = precip_probs[i] if i < len(precip_probs) else 100.0
            score = _score_hour(cloud, precip, moon_illumination)
            night_slots.append((dt, score, cloud))

    if not night_slots:
        return ApiRequestStargazingTimePost200Response(
            sky_condition="unknown",
            optimal_time_range=None,
        )

    best = max(night_slots, key=lambda x: x[1])
    avg_cloud = sum(s[2] for s in night_slots) / len(night_slots)

    return _build_response(best[0], _get_sky_condition(avg_cloud))


async def api_request_stargazing_time_post(
    req: Optional[ApiRequestStargazingTimePostRequest],
) -> ApiRequestStargazingTimePost200Response:
    if req is None or req.gps is None:
        raise HTTPException(status_code=400, detail="GPS location is required")

    lat = req.gps.latitude
    lon = req.gps.longitude
    target_date: date = req.target_date or date.today()
    cache_key = _get_cache_key(lat, lon, target_date)

    # 1. Try Redis cache first
    redis = _get_redis()
    if redis is not None:
        try:
            cached = redis.get(cache_key)
            if cached:
                logger.info(f"Cache hit for key: {cache_key}")
                payload = json.loads(cached)
                return ApiRequestStargazingTimePost200Response(
                    optimal_time_range=ApiRequestStargazingTimePost200ResponseOptimalTimeRange(
                        start_time=datetime.fromisoformat(payload["startTime"]),
                        end_time=datetime.fromisoformat(payload["endTime"]),
                    ) if payload.get("startTime") else None,
                    sky_condition=payload.get("skyCondition"),
                )
        except Exception as e:
            logger.warning(f"Cache read failed, falling through to API: {e}")

    # 2. Cache miss — call Open-Meteo
    logger.info(f"Cache miss for key: {cache_key}, fetching from Open-Meteo")
    result = await fetch_and_score(lat, lon, target_date)

    # 3. Write result back to cache
    if redis is not None:
        try:
            payload = {"skyCondition": result.sky_condition}
            if result.optimal_time_range:
                payload["startTime"] = result.optimal_time_range.start_time.isoformat()
                payload["endTime"] = result.optimal_time_range.end_time.isoformat()
            redis.set(cache_key, json.dumps(payload), ex=CACHE_TTL_SECONDS)
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

    return result
