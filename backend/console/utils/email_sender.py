import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.config import settings
from backend.constant.email import (
    EMAIL_SUBJECT,
    VERIFICATION_EMAIL_TEXT_TEMPLATE,
    VERIFICATION_EMAIL_HTML_TEMPLATE,
    RECOMMENDATION_EMAIL_SUBJECT,
    RECOMMENDATION_EMAIL_TEXT_TEMPLATE,
    RECOMMENDATION_EMAIL_HTML_TEMPLATE,
)

logger = logging.getLogger(__name__)


def send_verification_email(to_email: str, code: str) -> bool:
    """
    发送验证码邮件。

    :param to_email: 收件人邮箱
    :param code: 6位验证码
    :return: 是否发送成功
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = EMAIL_SUBJECT
        msg["From"] = settings.smtp_from_email
        msg["To"] = to_email

        # 纯文本内容
        text_content = VERIFICATION_EMAIL_TEXT_TEMPLATE.format(code=code)

        # HTML 内容（更美观）
        html_content = VERIFICATION_EMAIL_HTML_TEMPLATE.format(code=code)

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, to_email, msg.as_string())

        print(f"Verification email sent to {to_email}")
        return True

    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False


def send_recommendation_email(
    to_email: str,
    username: str,
    date_str: str,
    moon_phase: str,
    moon_illumination: int,
    time_slots: list[dict],
    constellations: list[dict],
    tips: list[str],
) -> bool:
    """
    Send a personalised stargazing recommendation email.

    Args:
        to_email:           Recipient email address
        username:           Display name shown in the email
        date_str:           Human-readable date string, e.g. "2026-03-09"
        moon_phase:         Phase name, e.g. "Waxing Crescent"
        moon_illumination:  Integer percentage 0–100
        time_slots:         List of dicts with keys startTime, endTime, score, skyCondition
        constellations:     List of dicts with keys name, reason
        tips:               List of plain-text tip strings
    """
    try:
        # --- plain text ---
        slot_lines = "\n".join(
            f"  • {s['startTime']} – {s['endTime']}  "
            f"[{s.get('skyCondition', '')}]  score {s.get('score', 0):.0f}/100"
            for s in time_slots
        ) or "  No suitable windows found for tonight."

        const_lines = "\n".join(
            f"  • {c['name']}: {c['reason']}"
            for c in constellations
        ) or "  —"

        tip_lines = "\n".join(f"  • {t}" for t in tips) or "  —"

        text_body = RECOMMENDATION_EMAIL_TEXT_TEMPLATE.format(
            username=username,
            date=date_str,
            moon_phase=moon_phase,
            moon_illumination=moon_illumination,
            time_slots=slot_lines,
            constellations=const_lines,
            tips=tip_lines,
        )

        # --- HTML ---
        def _slot_rows(slots):
            if not slots:
                return "<p>No suitable windows found for tonight.</p>"
            rows = "".join(
                f"<tr>"
                f"<td style='padding:4px 8px'>{s['startTime']} – {s['endTime']}</td>"
                f"<td style='padding:4px 8px'>{s.get('skyCondition','')}</td>"
                f"<td style='padding:4px 8px;text-align:right'>{s.get('score', 0):.0f}/100</td>"
                f"</tr>"
                for s in slots
            )
            return (
                "<table style='width:100%;border-collapse:collapse;font-size:14px'>"
                "<tr style='background:#f0f0f0'>"
                "<th style='padding:4px 8px;text-align:left'>Window</th>"
                "<th style='padding:4px 8px;text-align:left'>Sky</th>"
                "<th style='padding:4px 8px;text-align:right'>Score</th>"
                "</tr>"
                + rows
                + "</table>"
            )

        def _list_items(items, key_name, key_reason):
            if not items:
                return "<p>—</p>"
            return "<ul>" + "".join(
                f"<li><strong>{i[key_name]}</strong>: {i[key_reason]}</li>"
                for i in items
            ) + "</ul>"

        def _tip_items(tip_list):
            if not tip_list:
                return "<p>—</p>"
            return "<ul>" + "".join(f"<li>{t}</li>" for t in tip_list) + "</ul>"

        html_body = RECOMMENDATION_EMAIL_HTML_TEMPLATE.format(
            username=username,
            date=date_str,
            moon_phase=moon_phase,
            moon_illumination=moon_illumination,
            time_slots_html=_slot_rows(time_slots),
            constellations_html=_list_items(constellations, "name", "reason"),
            tips_html=_tip_items(tips),
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = RECOMMENDATION_EMAIL_SUBJECT
        msg["From"] = settings.smtp_from_email
        msg["To"] = to_email
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, to_email, msg.as_string())

        logger.info(f"Recommendation email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send recommendation email to {to_email}: {e}")
        return False