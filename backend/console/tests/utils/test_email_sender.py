from backend.console.utils.email_sender import send_recommendation_email


def test_send_recommendation_email_uses_fallback_site(monkeypatch):
    captured = {}

    def mock_send_email(subject, to_email, text_content, html_content):
        captured["subject"] = subject
        captured["to_email"] = to_email
        captured["text_content"] = text_content
        captured["html_content"] = html_content
        return True

    monkeypatch.setattr(
        "backend.console.utils.email_sender.send_email",
        mock_send_email,
    )

    recommendation = {
        "username": "alice",
        "weather": {
            "temperature": 18.2,
            "humidity": 60,
            "cloud_cover": 10,
            "precipitation_probability": 5,
            "visibility": 16000,
            "wind_speed": 2.0,
            "summary": "The cloud cover is low tonight, making it a good time for stargazing.",
        },
        "recommended_site": None,
    }

    result = send_recommendation_email("alice@example.com", recommendation)

    assert result is True
    assert captured["to_email"] == "alice@example.com"
    assert "No suitable site found" in captured["text_content"]
    assert "No suitable site found" in captured["html_content"]
