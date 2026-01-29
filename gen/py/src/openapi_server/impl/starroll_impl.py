from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.token_response import TokenResponse

from openapi_server.models.user_response import UserResponse 
from openapi_server.models.user_auth import UserAuth

# 导入你写的 handler
from backend.console.handler.user_login import api_user_login_post
from backend.console.handler.user_register import api_user_reg_post
# ... 原有的导入 ...
from backend.console.handler.user_delete import api_delete_user_post
from backend.console.handler.user_change_password import api_change_password_post
from openapi_server.models.change_password_request import ChangePasswordRequest

class StarrollApiImpl(BaseDefaultApi):
    async def api_user_login_post(
        self,
        user_auth: UserAuth,
    ) -> TokenResponse:
        # 将业务逻辑委托给服务层
        return await api_user_login_post(user_auth)
    async def api_user_reg_post(
        self,
        user_auth: UserAuth,
    ) -> UserResponse:
        return await api_user_reg_post(user_auth)
    async def api_delete_user_post(self, user_auth: UserAuth):
        return await api_delete_user_post(user_auth)
    async def api_change_password_post(self, change_password_request: ChangePasswordRequest):
        return await api_change_password_post(change_password_request)