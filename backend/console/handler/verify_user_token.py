from openapi_server.models.user_response import UserResponse
from backend.console.utils.auth import get_current_token_payload


async def api_verify_user_token_post() -> UserResponse:
    payload = get_current_token_payload()
    user_id = str(payload.get("user_id"))
    username = payload.get("user_name")
    return UserResponse(user_id=user_id, username=username)
