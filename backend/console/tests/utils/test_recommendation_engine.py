from types import SimpleNamespace

from backend.console.utils.recommendation_engine import (
    build_recommendation,
    build_weather_summary,
    calculate_distance_km,
    select_best_observation_site,
)


def test_calculate_distance_km():
    distance = calculate_distance_km(30.2741, 120.1551, 30.2741, 120.1551)

    assert distance == 0


def test_build_weather_summary_good_weather():
    summary, score = build_weather_summary({
        "cloud_cover": 10,
        "precipitation_probability": 5,
        "visibility": 16000,
    })

    assert "good time for stargazing" in summary
    assert score >= 80


def test_select_best_observation_site():
    weather = {
        "cloud_cover": 10,
        "precipitation_probability": 5,
        "visibility": 16000,
    }
    sites = [
        SimpleNamespace(
            id=1,
            name="Near Dark Site",
            latitude=30.28,
            longitude=120.16,
            description="Good nearby site",
            light_pollution_score=20,
        ),
        SimpleNamespace(
            id=2,
            name="Far Site",
            latitude=31.50,
            longitude=121.90,
            description="Too far away",
            light_pollution_score=5,
        ),
    ]

    best_site = select_best_observation_site(30.2741, 120.1551, weather, sites)

    assert best_site is not None
    assert best_site["name"] == "Near Dark Site"
    assert best_site["distance_km"] < 5


def test_build_recommendation():
    weather = {
        "temperature": 18.2,
        "humidity": 60,
        "precipitation_probability": 5,
        "cloud_cover": 10,
        "wind_speed": 2.0,
        "visibility": 16000,
    }
    sites = [
        SimpleNamespace(
            id=1,
            name="Near Dark Site",
            latitude=30.28,
            longitude=120.16,
            description="Good nearby site",
            light_pollution_score=20,
        ),
    ]

    recommendation = build_recommendation(30.2741, 120.1551, weather, sites)

    assert recommendation["weather"]["score"] >= 80
    assert recommendation["recommended_site"]["name"] == "Near Dark Site"
