VERIFICATION_CODE_LENGTH = 6
VERIFICATION_CODE_EXPIRE_MINUTES = 10
EMAIL_SUBJECT = "StarRoll - Password Reset Verification Code"
RECOMMENDATION_EMAIL_SUBJECT = "StarRoll - Tonight's Stargazing Recommendation"

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

RECOMMENDATION_EMAIL_TEXT_TEMPLATE = """Hello {username},

Here is your StarRoll stargazing recommendation for tonight.

Weather:
- Temperature: {temperature} C
- Humidity: {humidity}%
- Cloud cover: {cloud_cover}%
- Precipitation probability: {precipitation_probability}%
- Visibility: {visibility} m
- Wind speed: {wind_speed} km/h
- Summary: {weather_summary}

Recommended observation site:
- Name: {site_name}
- Distance: {distance_km} km
- Description: {site_description}
- Reason: {site_reason}

Best regards,
StarRoll Team
"""

RECOMMENDATION_EMAIL_HTML_TEMPLATE = """
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #333;">Tonight's Stargazing Recommendation</h2>
    <p>Hello {username},</p>
    <p>Here is your weather-based stargazing recommendation for tonight.</p>
    <h3>Weather</h3>
    <ul>
        <li>Temperature: {temperature} C</li>
        <li>Humidity: {humidity}%</li>
        <li>Cloud cover: {cloud_cover}%</li>
        <li>Precipitation probability: {precipitation_probability}%</li>
        <li>Visibility: {visibility} m</li>
        <li>Wind speed: {wind_speed} km/h</li>
    </ul>
    <p><strong>{weather_summary}</strong></p>
    <h3>Recommended Observation Site</h3>
    <p><strong>{site_name}</strong></p>
    <p>Distance: {distance_km} km</p>
    <p>{site_description}</p>
    <p>{site_reason}</p>
    <p>Best regards,<br/>StarRoll Team</p>
</body>
</html>
"""