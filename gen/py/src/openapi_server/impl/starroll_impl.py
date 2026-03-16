from openapi_server.apis.default_api_base import BaseDefaultApi
from openapi_server.models.token_response import TokenResponse

from openapi_server.models.user_response import UserResponse
from openapi_server.models.user_auth import UserAuth

from backend.console.handler.user_login import api_user_login_post
from backend.console.handler.user_register import api_user_reg_post
from backend.console.handler.user_delete import api_delete_user_post

from backend.console.handler.edit_profile import api_edit_profile_post
from backend.console.handler.update_last_gps import api_update_last_gps_post

from backend.console.handler.user_change_password import api_change_password_post
from backend.console.handler.create_identify_starts_job import api_create_identify_stars_job_post
from openapi_server.models.change_password_request import ChangePasswordRequest
from openapi_server.models.api_update_last_gps_post_request import ApiUpdateLastGpsPostRequest
from openapi_server.models.reset_password_send_code_request import ResetPasswordSendCodeRequest
from openapi_server.models.reset_password_request import ResetPasswordRequest

from openapi_server.models.profile_and_token import ProfileAndToken

from backend.console.handler.reset_password_send_code import api_reset_password_send_code_post as api_reset_password_send_code_post_handler
from backend.console.handler.reset_password import api_reset_password_post as api_reset_password_post_handler

from openapi_server.models.api_create_identify_stars_job_post_request import ApiCreateIdentifyStarsJobPostRequest

from openapi_server.models.api_list_identify_stars_jobs_post_request import ApiListIdentifyStarsJobsPostRequest
from openapi_server.models.api_list_identify_stars_jobs_post200_response import ApiListIdentifyStarsJobsPost200Response
from backend.console.handler.list_identify_stars_jobs import api_list_identify_stars_jobs_post

from openapi_server.models.api_get_identify_stars_job_result_post_request import ApiGetIdentifyStarsJobResultPostRequest
from openapi_server.models.api_get_identify_stars_job_result_post200_response import ApiGetIdentifyStarsJobResultPost200Response
from backend.console.handler.get_identify_stars_job_result import api_get_identify_stars_job_result_post

from openapi_server.models.profile_stats_request import ProfileStatsRequest
from openapi_server.models.profile_stats_response import ProfileStatsResponse
from backend.console.handler.profile_stats import api_get_profile_stats_post as api_get_profile_stats_post_handler

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

    async def api_update_last_gps_post(self, api_update_last_gps_post_request: ApiUpdateLastGpsPostRequest):
        return await api_update_last_gps_post(api_update_last_gps_post_request)

    async def api_create_identify_stars_job_post(self, api_create_identify_stars_job_post_request: ApiCreateIdentifyStarsJobPostRequest):
        return await api_create_identify_stars_job_post(api_create_identify_stars_job_post_request)

    async def api_list_identify_stars_jobs_post(self, api_list_identify_stars_jobs_post_request: ApiListIdentifyStarsJobsPostRequest) -> ApiListIdentifyStarsJobsPost200Response:
        return await api_list_identify_stars_jobs_post(api_list_identify_stars_jobs_post_request)

    async def api_reset_password_send_code_post(self, reset_password_send_code_request: ResetPasswordSendCodeRequest):
        return await api_reset_password_send_code_post_handler(reset_password_send_code_request)

    async def api_reset_password_post(self, reset_password_request: ResetPasswordRequest):
        return await api_reset_password_post_handler(reset_password_request)

    async def api_get_identify_stars_job_result_post(self, api_get_identify_stars_job_result_post_request: ApiGetIdentifyStarsJobResultPostRequest) -> ApiGetIdentifyStarsJobResultPost200Response:
        return await api_get_identify_stars_job_result_post(api_get_identify_stars_job_result_post_request)

    async def api_get_profile_stats_post(self, profile_stats_request: ProfileStatsRequest) -> ProfileStatsResponse:
        return await api_get_profile_stats_post_handler(profile_stats_request)
    
    async def api_health_get(self) -> None:
        return
