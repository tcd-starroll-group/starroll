from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.token_response import TokenResponse
from gen.py.src.openapi_server.models.user_auth import UserAuth
from backend.console.handler.user_login import api_user_login_post


class StarrollApiImpl(BaseDefaultApi):
    async def api_user_login_post(
        self,
        user_auth: UserAuth,
    ) -> TokenResponse:
        # 将业务逻辑委托给服务层
        return await api_user_login_post(user_auth)
