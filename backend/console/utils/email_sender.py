import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.config import settings
from backend.constant.email import EMAIL_SUBJECT


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
        text_content = f"""Hello,

Your StarRoll password reset verification code is:

    {code}

This code will expire in 10 minutes. If you did not request a password reset, please ignore this email.

Best regards,
StarRoll Team
"""

        # HTML 内容（更美观）
        html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #333;">StarRoll Password Reset</h2>
    <p>Hello,</p>
    <p>Your verification code is:</p>
    <div style="background: #f5f5f5; padding: 15px 25px; font-size: 28px;
                font-weight: bold; letter-spacing: 8px; text-align: center;
                border-radius: 8px; margin: 20px 0; color: #333;">
        {code}
    </div>
    <p>This code will expire in <strong>10 minutes</strong>.</p>
    <p style="color: #999; font-size: 12px;">
        If you did not request a password reset, please ignore this email.
    </p>
    <p>Best regards,<br/>StarRoll Team</p>
</body>
</html>
"""

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