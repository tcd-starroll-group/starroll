import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.config import settings
from backend.constant.email import (
    EMAIL_SUBJECT,
    VERIFICATION_EMAIL_TEXT_TEMPLATE,
    VERIFICATION_EMAIL_HTML_TEMPLATE,
)


def send_verification_email(to_email: str, code: str) -> bool:
    """
    Semd verification email

    :param to_email: receiver email adress
    :param code: 6digit verification code
    :return: boolean param for send success
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = EMAIL_SUBJECT
        msg["From"] = settings.smtp_from_email
        msg["To"] = to_email

        
        text_content = VERIFICATION_EMAIL_TEXT_TEMPLATE.format(code=code)

        
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