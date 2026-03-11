VERIFICATION_CODE_LENGTH = 6
VERIFICATION_CODE_EXPIRE_MINUTES = 10
EMAIL_SUBJECT = "StarRoll - Password Reset Verification Code"

RECOMMENDATION_EMAIL_SUBJECT = "StarRoll - Tonight's Stargazing Recommendation"

RECOMMENDATION_EMAIL_TEXT_TEMPLATE = """Hello {username},

Here is your personalised stargazing recommendation for tonight ({date}):

MOON PHASE
  {moon_phase} ({moon_illumination}% illuminated)

BEST TIME WINDOWS
{time_slots}

RECOMMENDED CONSTELLATIONS
{constellations}

TIPS
{tips}

Clear skies!
StarRoll Team
"""

RECOMMENDATION_EMAIL_HTML_TEMPLATE = """
<html>
<body style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;">
  <h2 style="color: #1a1a2e;">⭐ Tonight's Stargazing Recommendation</h2>
  <p>Hello <strong>{username}</strong>,</p>
  <p>Here is your personalised recommendation for <strong>{date}</strong>:</p>

  <h3 style="color: #16213e; border-bottom: 1px solid #eee; padding-bottom: 6px;">🌙 Moon Phase</h3>
  <p>{moon_phase} &mdash; <strong>{moon_illumination}%</strong> illuminated</p>

  <h3 style="color: #16213e; border-bottom: 1px solid #eee; padding-bottom: 6px;">🕐 Best Time Windows</h3>
  {time_slots_html}

  <h3 style="color: #16213e; border-bottom: 1px solid #eee; padding-bottom: 6px;">🔭 Recommended Constellations</h3>
  {constellations_html}

  <h3 style="color: #16213e; border-bottom: 1px solid #eee; padding-bottom: 6px;">💡 Tips</h3>
  {tips_html}

  <p style="margin-top: 30px; color: #555;">Clear skies!</p>
  <p><strong>StarRoll Team</strong></p>
  <hr style="border: none; border-top: 1px solid #eee; margin-top: 30px;" />
  <p style="color: #aaa; font-size: 11px;">
    You are receiving this email because you have an active StarRoll account.
  </p>
</body>
</html>
"""

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