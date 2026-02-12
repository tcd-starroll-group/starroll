from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.token_response import TokenResponse

from openapi_server.models.user_response import UserResponse
from openapi_server.models.user_auth import UserAuth

from backend.console.handler.user_login import api_user_login_post
from backend.console.handler.user_register import api_user_reg_post
from backend.console.handler.user_delete import api_delete_user_post

from backend.console.handler.edit_profile import api_edit_profile_post

from backend.console.handler.user_change_password import api_change_password_post
from backend.console.handler.create_identify_starts_job import api_create_identify_stars_job_post
from openapi_server.models.change_password_request import ChangePasswordRequest

from openapi_server.models.profile_and_token import ProfileAndToken


from openapi_server.models.api_create_identify_stars_job_post_request import ApiCreateIdentifyStarsJobPostRequest
from openapi_server.models.api_list_identify_stars_jobs_post_request import ApiListIdentifyStarsJobsPostRequest
from openapi_server.models.api_list_identify_stars_jobs_post200_response import ApiListIdentifyStarsJobsPost200Response
from backend.console.handler.list_identify_stars_jobs import api_list_identify_stars_jobs_post


class StarrollApiImpl(BaseDefaultApi):
    async def api_user_login_post(
        self,
        user_auth: UserAuth,
    ) -> TokenResponse:
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

    async def api_edit_profile_post(self, profile_and_token: ProfileAndToken):
        return await api_edit_profile_post(profile_and_token)

    async def api_create_identify_stars_job_post(self, api_create_identify_stars_job_post_request: ApiCreateIdentifyStarsJobPostRequest):
        return await api_create_identify_stars_job_post(api_create_identify_stars_job_post_request)

    async def api_list_identify_stars_jobs_post(self, api_list_identify_stars_jobs_post_request: ApiListIdentifyStarsJobsPostRequest) -> ApiListIdentifyStarsJobsPost200Response:
        return await api_list_identify_stars_jobs_post(api_list_identify_stars_jobs_post_request)
