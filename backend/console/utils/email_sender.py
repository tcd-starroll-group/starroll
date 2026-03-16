import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.config import settings
from backend.constant.email import (
    EMAIL_SUBJECT,
    RECOMMENDATION_EMAIL_HTML_TEMPLATE,
    RECOMMENDATION_EMAIL_SUBJECT,
    RECOMMENDATION_EMAIL_TEXT_TEMPLATE,
    VERIFICATION_EMAIL_TEXT_TEMPLATE,
    VERIFICATION_EMAIL_HTML_TEMPLATE,
)


def send_email(subject: str, to_email: str, text_content: str, html_content: str) -> bool:
    """Send an email using the configured SMTP service."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from_email
        msg["To"] = to_email

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, to_email, msg.as_string())

        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False


def send_verification_email(to_email: str, code: str) -> bool:
    """
    发送验证码邮件。

    :param to_email: 收件人邮箱
    :param code: 6位验证码
    :return: 是否发送成功
    """
    text_content = VERIFICATION_EMAIL_TEXT_TEMPLATE.format(code=code)
    html_content = VERIFICATION_EMAIL_HTML_TEMPLATE.format(code=code)
    return send_email(EMAIL_SUBJECT, to_email, text_content, html_content)


def send_recommendation_email(to_email: str, recommendation: dict) -> bool:
    """Send a recommendation email with current weather and the best site."""
    site = recommendation.get("recommended_site") or {
        "name": "No suitable site found",
        "distance_km": "-",
        "description": "No nearby observation site is currently available.",
        "reason": "The project site list has no nearby active candidate.",
    }
    weather = recommendation["weather"]
    content = {
        "username": recommendation.get("username", "StarRoll user"),
        "temperature": weather.get("temperature", "-"),
        "humidity": weather.get("humidity", "-"),
        "cloud_cover": weather.get("cloud_cover", "-"),
        "precipitation_probability": weather.get("precipitation_probability", "-"),
        "visibility": weather.get("visibility", "-"),
        "wind_speed": weather.get("wind_speed", "-"),
        "weather_summary": weather.get("summary", ""),
        "site_name": site.get("name", "-"),
        "distance_km": site.get("distance_km", "-"),
        "site_description": site.get("description", ""),
        "site_reason": site.get("reason", ""),
    }
    text_content = RECOMMENDATION_EMAIL_TEXT_TEMPLATE.format(**content)
    html_content = RECOMMENDATION_EMAIL_HTML_TEMPLATE.format(**content)
    return send_email(
        RECOMMENDATION_EMAIL_SUBJECT,
        to_email,
        text_content,
        html_content,
    )