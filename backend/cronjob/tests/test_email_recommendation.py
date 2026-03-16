from unittest.mock import MagicMock

from backend.cronjob.email_recommendation import _send_recommendations


def test_send_recommendations(monkeypatch):
    user_with_gps = MagicMock()
    user_with_gps.username = "alice"
    user_with_gps.email = "alice@example.com"

    user_without_gps = MagicMock()
    user_without_gps.username = "bob"
    user_without_gps.email = "bob@example.com"

    monkeypatch.setattr(
        "backend.cronjob.email_recommendation.User.list_with_email",
        lambda db_session: [user_with_gps, user_without_gps],
    )
    monkeypatch.setattr(
        "backend.cronjob.email_recommendation.generate_recommendation_for_user",
        lambda db_session, user: None if user.username == "bob" else {
            "username": user.username,
            "weather": {"summary": "good"},
            "recommended_site": {"name": "site"},
        },
    )
    send_mock = MagicMock(return_value=True)
    monkeypatch.setattr(
        "backend.cronjob.email_recommendation.send_recommendation_email",
        send_mock,
    )

    result = _send_recommendations(MagicMock())

    assert result == {
        "processed": 2,
        "sent": 1,
        "skipped": 1,
        "failed": 0,
    }
    send_mock.assert_called_once_with(
        "alice@example.com",
        {
            "username": "alice",
            "weather": {"summary": "good"},
            "recommended_site": {"name": "site"},
        },
    )


def test_send_recommendations_send_failure(monkeypatch):
    user = MagicMock()
    user.username = "alice"
    user.email = "alice@example.com"

    monkeypatch.setattr(
        "backend.cronjob.email_recommendation.User.list_with_email",
        lambda db_session: [user],
    )
    monkeypatch.setattr(
        "backend.cronjob.email_recommendation.generate_recommendation_for_user",
        lambda db_session, current_user: {
            "username": current_user.username,
            "weather": {"summary": "good"},
            "recommended_site": {"name": "site"},
        },
    )
    monkeypatch.setattr(
        "backend.cronjob.email_recommendation.send_recommendation_email",
        lambda email, recommendation: False,
    )

    result = _send_recommendations(MagicMock())

    assert result == {
        "processed": 1,
        "sent": 0,
        "skipped": 0,
        "failed": 1,
    }


def test_send_recommendations_generation_exception(monkeypatch):
    user = MagicMock()
    user.username = "alice"
    user.email = "alice@example.com"

    monkeypatch.setattr(
        "backend.cronjob.email_recommendation.User.list_with_email",
        lambda db_session: [user],
    )

    def _raise_error(db_session, current_user):
        raise RuntimeError("unexpected error")

    monkeypatch.setattr(
        "backend.cronjob.email_recommendation.generate_recommendation_for_user",
        _raise_error,
    )

    result = _send_recommendations(MagicMock())

    assert result == {
        "processed": 1,
        "sent": 0,
        "skipped": 0,
        "failed": 1,
    }
