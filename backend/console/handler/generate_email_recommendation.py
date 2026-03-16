from typing import Any, Dict, Optional, Tuple

from backend.console.dal.rds.observation_site import ObservationSite
from backend.console.utils.recommendation_engine import build_recommendation
from backend.console.utils.weather_client import get_current_weather


def generate_recommendation_for_user(db, user) -> Optional[Dict[str, Any]]:
    """Generate recommendation content for a user with stored GPS data."""
    gps = extract_last_gps(user)
    if gps is None:
        return None

    weather = get_current_weather(gps["latitude"], gps["longitude"])
    sites = ObservationSite.list_active(db)
    recommendation = build_recommendation(
        user_latitude=gps["latitude"],
        user_longitude=gps["longitude"],
        weather=weather,
        sites=sites,
    )
    recommendation["email"] = user.email
    recommendation["username"] = user.username
    recommendation["gps"] = gps
    return recommendation


def extract_last_gps(user: Any) -> Optional[Dict[str, float]]:
    """Read GPS from user.last_gps, with profile.last_gps as fallback."""
    gps = getattr(user, "last_gps", None)
    if not isinstance(gps, dict):
        profile = getattr(user, "profile", None)
        if not isinstance(profile, dict):
            return None
        gps = profile.get("last_gps")
        if not isinstance(gps, dict):
            return None

    latitude, longitude = _parse_coordinates(gps)
    if latitude is None or longitude is None:
        return None

    return {
        "latitude": latitude,
        "longitude": longitude,
    }


def _parse_coordinates(gps: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    try:
        return float(gps.get("latitude")), float(gps.get("longitude"))
    except (TypeError, ValueError):
        return None, None
