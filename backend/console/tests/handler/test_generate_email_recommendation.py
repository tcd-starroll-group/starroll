import hashlib

from backend.console.dal.rds.user import User
from backend.console.handler.generate_email_recommendation import (
    extract_last_gps,
    generate_recommendation_for_user,
)


def test_extract_last_gps():
    class UserLike:
        last_gps = {
            "latitude": 30.2741,
            "longitude": 120.1551,
        }
        profile = None

    gps = extract_last_gps(UserLike())

    assert gps == {"latitude": 30.2741, "longitude": 120.1551}


def test_extract_last_gps_falls_back_to_profile():
    class UserLike:
        last_gps = None
        profile = {
            "last_gps": {
                "latitude": 31.2304,
                "longitude": 121.4737,
            }
        }

    gps = extract_last_gps(UserLike())

    assert gps == {"latitude": 31.2304, "longitude": 121.4737}


def test_extract_last_gps_invalid_returns_none():
    class UserLike:
        last_gps = {
            "latitude": "invalid",
            "longitude": 120.1551,
        }
        profile = None

    gps = extract_last_gps(UserLike())

    assert gps is None


def test_generate_recommendation_for_user(db_session, monkeypatch):
    hashed_password = hashlib.sha256("password123".encode()).hexdigest()
    user = User.create(db_session, "alice", hashed_password, "alice@example.com")
    User.update_last_gps(db_session, "alice", {
        "latitude": 30.2741,
        "longitude": 120.1551,
    })
    user = User.get_by_username(db_session, "alice")

    monkeypatch.setattr(
        "backend.console.handler.generate_email_recommendation.get_current_weather",
        lambda latitude, longitude: {
            "temperature": 18.2,
            "humidity": 60,
            "precipitation_probability": 5,
            "cloud_cover": 10,
            "wind_speed": 2.0,
            "visibility": 16000,
            "latitude": latitude,
            "longitude": longitude,
        },
    )

    recommendation = generate_recommendation_for_user(db_session, user)

    assert recommendation is not None
    assert recommendation["email"] == "alice@example.com"
    assert recommendation["weather"]["score"] >= 80
    assert recommendation["recommended_site"] is not None
