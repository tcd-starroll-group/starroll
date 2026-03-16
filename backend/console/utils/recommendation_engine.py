import math
from typing import Any, Dict, Iterable, Optional, Tuple


MAX_RECOMMEND_DISTANCE_KM = 80.0


def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float,
) -> float:
    """Calculate great-circle distance between two GPS points."""
    earth_radius_km = 6371.0

    lat1 = math.radians(latitude1)
    lon1 = math.radians(longitude1)
    lat2 = math.radians(latitude2)
    lon2 = math.radians(longitude2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius_km * c


def build_weather_summary(weather: Dict[str, Any]) -> Tuple[str, int]:
    """Convert raw weather fields into a stargazing conclusion and score."""
    cloud_cover = _safe_number(weather.get("cloud_cover"))
    precipitation_probability = _safe_number(
        weather.get("precipitation_probability"))
    visibility = _safe_number(weather.get("visibility"))

    score = 100
    score -= min(cloud_cover, 100) * 0.6
    score -= min(precipitation_probability, 100) * 0.5

    if visibility < 5000:
        score -= 20
    elif visibility < 10000:
        score -= 10

    score = max(0, min(100, int(round(score))))

    if cloud_cover <= 20 and precipitation_probability <= 20:
        summary = "The cloud cover is low tonight, making it a good time for stargazing."
    elif cloud_cover <= 50 and precipitation_probability <= 40:
        summary = "The weather is so-so tonight.。"
    else:
        summary = "Tonight, cloud cover or precipitation will be significant, making it unsuitable for stargazing."

    return summary, score


def select_best_observation_site(
    user_latitude: float,
    user_longitude: float,
    weather: Dict[str, Any],
    sites: Iterable[Any],
) -> Optional[Dict[str, Any]]:
    """Pick the best nearby observation site using a simple rule-based score."""
    summary, weather_score = build_weather_summary(weather)
    best_site = None
    best_score = None

    for site in sites:
        distance_km = calculate_distance_km(
            user_latitude,
            user_longitude,
            float(site.latitude),
            float(site.longitude),
        )
        if distance_km > MAX_RECOMMEND_DISTANCE_KM:
            continue

        site_base_score = 100 - min(float(site.light_pollution_score), 100.0)
        distance_penalty = distance_km * 0.8
        weather_bonus = weather_score * 0.2
        final_score = site_base_score - distance_penalty + weather_bonus

        if best_score is None or final_score > best_score:
            best_score = final_score
            best_site = {
                "id": site.id,
                "name": site.name,
                "latitude": float(site.latitude),
                "longitude": float(site.longitude),
                "description": site.description,
                "light_pollution_score": float(site.light_pollution_score),
                "distance_km": round(distance_km, 2),
                "reason": (
                    f"{summary} The location is relatively close, and its light pollution rating is "
                    f"{float(site.light_pollution_score):.0f}。"
                ),
                "score": round(final_score, 2),
            }

    return best_site


def build_recommendation(
    user_latitude: float,
    user_longitude: float,
    weather: Dict[str, Any],
    sites: Iterable[Any],
) -> Dict[str, Any]:
    """Build the final payload used by the email recommendation task."""
    weather_summary, weather_score = build_weather_summary(weather)
    recommended_site = select_best_observation_site(
        user_latitude=user_latitude,
        user_longitude=user_longitude,
        weather=weather,
        sites=sites,
    )

    return {
        "weather": {
            **weather,
            "summary": weather_summary,
            "score": weather_score,
        },
        "recommended_site": recommended_site,
    }


def _safe_number(value: Any) -> float:
    if value is None:
        return 100.0
    return float(value)
