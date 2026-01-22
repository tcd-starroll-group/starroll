from gen.py.src.openapi_server.models.user_auth import UserAuth
from gen.py.src.openapi_server.models.token_response import TokenResponse
from fastapi import Body


async def api_user_login_post(
    user_auth: UserAuth = Body(None, description=""),
) -> TokenResponse:
    print(user_auth)
    return TokenResponse(token="xxx", expires_in=60)
