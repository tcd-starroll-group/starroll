from gen.py.src.openapi_server.models.user_auth import UserAuth
from gen.py.src.openapi_server.models.user_response import UserResponse
from fastapi import Body


async def api_user_reg_post(
    user_auth: UserAuth,
) -> UserResponse:
    print(user_auth)
    
    return UserResponse(id=1, name=user_auth.name, email=user_auth.email)