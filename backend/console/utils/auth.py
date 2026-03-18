import jwt
import datetime
import logging
from contextvars import ContextVar, Token
from typing import Dict, Any, Tuple
from backend.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

_current_token_payload: ContextVar[Dict[str, Any] | None] = ContextVar(
    "current_token_payload",
    default=None,
)


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


def verify_user_id_and_token(token: str, user_id: str) -> None:
    """
    Verify the access token and ensure the user_id matches the token's user_id.

    Args:
        token: The JWT token string to verify.
        user_id: The user ID to match against the token's payload.

    Raises:
        HTTPException: If the token is invalid, expired, or the user_id does not match.
    """
    payload, is_valid = verify_access_token(token)
    if not is_valid or not payload:
        logger.error("Invalid or expired token")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    token_user_id = payload.get("user_id")
    if not token_user_id or str(token_user_id) != str(user_id):
        logger.error(
            f"Token user_id mismatch: token has {token_user_id}, request has {user_id}")
        raise HTTPException(status_code=403, detail="User ID mismatch")

    logger.info(f"Token verification successful for user_id: {user_id}")


def set_current_token_payload(payload: Dict[str, Any]) -> Token:
    return _current_token_payload.set(payload)


def reset_current_token_payload(token: Token) -> None:
    _current_token_payload.reset(token)


def get_current_token_payload() -> Dict[str, Any]:
    payload = _current_token_payload.get()
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


def get_current_user_id() -> str:
    payload = get_current_token_payload()
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return str(user_id)
