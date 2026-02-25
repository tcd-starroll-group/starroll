VERIFICATION_CODE_LENGTH = 6
VERIFICATION_CODE_EXPIRE_MINUTES = 10
EMAIL_SUBJECT = "StarRoll - Password Reset Verification Code"

VERIFICATION_EMAIL_TEXT_TEMPLATE = """Hello,

Your StarRoll password reset verification code is:

    {code}

This code will expire in 10 minutes. If you did not request a password reset, please ignore this email.

Best regards,
StarRoll Team
"""

VERIFICATION_EMAIL_HTML_TEMPLATE = """
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