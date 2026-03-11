"""
Precompute stargazing recommendations for a set of well-known dark-sky locations.
Results are written to Redis so API responses are instant cache hits.
"""

import asyncio
import json
import logging
from datetime import date, datetime, timedelta

from backend.console.dal.cache.client import RedisClient
from backend.console.handler.request_stargazing_time import (
    CACHE_TTL_SECONDS,
    _get_cache_key,
    _get_sky_condition,
    _calculate_moon_illumination,
    fetch_and_score,
)
from backend.config.settings import Settings

logger = logging.getLogger(__name__)

# Famous dark-sky / popular stargazing locations around the world
POPULAR_LOCATIONS = [
    {"name": "Cherry Springs State Park, USA", "lat": 41.6626, "lon": -77.8218},
    {"name": "Mauna Kea, Hawaii", "lat": 19.8207, "lon": -155.4681},
    {"name": "Atacama Desert, Chile", "lat": -23.0, "lon": -67.0},
    {"name": "Namib-Naukluft, Namibia", "lat": -24.7, "lon": 15.9},
    {"name": "Jasper National Park, Canada", "lat": 52.8734, "lon": -117.954},
    {"name": "Exmoor, UK", "lat": 51.1517, "lon": -3.6018},
    {"name": "Brecon Beacons, Wales", "lat": 51.8833, "lon": -3.4333},
    {"name": "Aoraki Mackenzie, New Zealand", "lat": -43.9333, "lon": 170.4500},
    {"name": "NamibRand Nature Reserve, Namibia", "lat": -25.0, "lon": 16.0},
    {"name": "Kerry, Ireland", "lat": 52.0, "lon": -9.85},
]


def precompute_stargazing_handler():
    """
    Synchronous entry point for APScheduler.
    Runs the async precompute logic in a new event loop.
    """
    try:
        asyncio.run(_precompute_all())
    except Exception as e:
        logger.error(f"Precompute stargazing job failed: {e}", exc_info=True)


async def _precompute_all():
    """Precompute recommendations for today and tomorrow for all popular locations."""
    try:
        redis = RedisClient.get_instance(Settings())
    except Exception as e:
        logger.warning(f"Redis unavailable, skipping precompute: {e}")
        return

    dates_to_compute = [date.today(), date.today() + timedelta(days=1)]

    for location in POPULAR_LOCATIONS:
        for target_date in dates_to_compute:
            await _precompute_one(redis, location, target_date)


async def _precompute_one(redis: RedisClient, location: dict, target_date: date):
    lat = location["lat"]
    lon = location["lon"]
    name = location["name"]
    cache_key = _get_cache_key(lat, lon, target_date)

    # Skip if already cached
    try:
        if redis.exists(cache_key):
            logger.debug(f"Already cached: {name} / {target_date}")
            return
    except Exception as e:
        logger.warning(f"Redis exists check failed for {name}: {e}")

    try:
        result = await fetch_and_score(lat, lon, target_date)

        payload = {"skyCondition": result.sky_condition}
        if result.optimal_time_range:
            payload["startTime"] = result.optimal_time_range.start_time.isoformat()
            payload["endTime"] = result.optimal_time_range.end_time.isoformat()

        redis.set(cache_key, json.dumps(payload), ex=CACHE_TTL_SECONDS)
        logger.info(f"Precomputed: {name} / {target_date} -> {result.sky_condition}")

    except Exception as e:
        logger.error(f"Failed to precompute {name} / {target_date}: {e}")
