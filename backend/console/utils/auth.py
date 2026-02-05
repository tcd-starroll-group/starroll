import jwt
import datetime
import logging
from typing import Dict, Any, Tuple
from backend.config import settings

logger = logging.getLogger(__name__)


def create_access_token(data: dict) -> str:
    """Generate a new JWT access token"""
    to_encode = data.copy()

    # Set expiration time
    expire = datetime.datetime.now(
        datetime.timezone.utc) + datetime.timedelta(hours=settings.jwt_expire_hours)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_access_token(token: str) -> Tuple[Dict[str, Any] | None, bool]:
    """
    Verify and decode a JWT access token.

    Args:
        token: The JWT token string to verify

    Returns:
        A tuple of (payload, is_valid) where:
        - payload: The decoded token payload as a dictionary, or None if verification failed
        - is_valid: Boolean indicating whether the token is valid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        logger.debug("Token verification successful")
        return payload, True
    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: Token has expired")
        return None, False
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return None, False
