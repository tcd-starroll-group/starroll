from typing import Any, Dict

import requests

from backend.config import settings


def get_current_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    """Fetch current weather details from Open-Meteo."""
    response = requests.get(
        settings.weather_api_endpoint,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join([
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation_probability",
                "cloud_cover",
                "wind_speed_10m",
                "visibility",
            ]),
            "timezone": "auto",
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    current = data.get("current") or {}

    return {
        "latitude": latitude,
        "longitude": longitude,
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "precipitation_probability": current.get("precipitation_probability"),
        "cloud_cover": current.get("cloud_cover"),
        "wind_speed": current.get("wind_speed_10m"),
        "visibility": current.get("visibility"),
        "timezone": data.get("timezone"),
        "current_time": current.get("time"),
    }
