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
from openapi_server.models.update_last_gps_request import UpdateLastGpsRequest
from openapi_server.models.reset_password_send_code_request import ResetPasswordSendCodeRequest
from openapi_server.models.reset_password_request import ResetPasswordRequest

from openapi_server.models.profile_and_token import ProfileAndToken
from openapi_server.models.pagination_query import PaginationQuery
from openapi_server.models.api_create_blog_post_request import ApiCreateBlogPostRequest
from openapi_server.models.api_create_blog_post200_response import ApiCreateBlogPost200Response
from openapi_server.models.blog_id import BlogID
from openapi_server.models.blogs_list import BlogsList
from openapi_server.models.api_like_blog_post200_response import ApiLikeBlogPost200Response
from openapi_server.models.api_list_star_blogs_post_request import ApiListStarBlogsPostRequest
from openapi_server.models.api_report_blog_post_request import ApiReportBlogPostRequest
from openapi_server.models.api_comment_blog_post_request import ApiCommentBlogPostRequest
from openapi_server.models.api_comment_blog_post200_response import ApiCommentBlogPost200Response
from openapi_server.models.blog import Blog

from backend.console.handler.reset_password_send_code import api_reset_password_send_code_post as api_reset_password_send_code_post_handler
from backend.console.handler.reset_password import api_reset_password_post as api_reset_password_post_handler
from backend.console.handler.create_blog import api_create_blog_post
from backend.console.handler.delete_blog import api_delete_blog_post
from backend.console.handler.like_blog import api_like_blog_post
from backend.console.handler.list_saved_blogs import api_list_saved_blogs_post
from backend.console.handler.list_star_blogs import api_list_star_blogs_post
from backend.console.handler.list_user_blogs import api_list_user_blogs_post
from backend.console.handler.report_blog import api_report_blog_post
from backend.console.handler.save_blog import api_save_blog_post
from backend.console.handler.comment_blog import api_comment_blog_post
from backend.console.handler.view_blog import api_view_blog_post

from openapi_server.models.api_create_identify_stars_job_post_request import ApiCreateIdentifyStarsJobPostRequest

from openapi_server.models.api_list_identify_stars_jobs_post200_response import ApiListIdentifyStarsJobsPost200Response
from backend.console.handler.list_identify_stars_jobs import api_list_identify_stars_jobs_post

from openapi_server.models.api_get_identify_stars_job_result_post_request import ApiGetIdentifyStarsJobResultPostRequest
from openapi_server.models.identify_stars_job_result import IdentifyStarsJobResult
from backend.console.handler.get_identify_stars_job_result import api_get_identify_stars_job_result_post

from openapi_server.models.profile_stats_response import ProfileStatsResponse
from backend.console.handler.profile_stats import api_get_profile_stats_post as api_get_profile_stats_post_handler
from openapi_server.models.common_message import CommonMessage
from openapi_server.models.common_id import CommonID
from openapi_server.models.star_message import StarMessage
from backend.console.handler.check_login_status import api_check_login_status_post
from backend.console.handler.create_star_message import api_create_star_message_post as api_create_star_message_post_handler
from backend.console.handler.get_star_message import api_get_star_message_post as api_get_star_message_post_handler
from openapi_server.models.star_message import StarMessage
from openapi_server.models.common_id import CommonID
from backend.console.handler.create_star_message import api_create_star_message_post
from backend.console.handler.get_star_message import api_get_star_message_post


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

    async def api_update_last_gps_post(self, api_update_last_gps_post_request: UpdateLastGpsRequest):
        return await api_update_last_gps_post(api_update_last_gps_post_request)

    async def api_create_identify_stars_job_post(self, api_create_identify_stars_job_post_request: ApiCreateIdentifyStarsJobPostRequest):
        return await api_create_identify_stars_job_post(api_create_identify_stars_job_post_request)

    async def api_list_identify_stars_jobs_post(self, api_list_identify_stars_jobs_post_request: PaginationQuery) -> ApiListIdentifyStarsJobsPost200Response:
        return await api_list_identify_stars_jobs_post(api_list_identify_stars_jobs_post_request)

    async def api_reset_password_send_code_post(self, reset_password_send_code_request: ResetPasswordSendCodeRequest):
        return await api_reset_password_send_code_post_handler(reset_password_send_code_request)

    async def api_reset_password_post(self, reset_password_request: ResetPasswordRequest):
        return await api_reset_password_post_handler(reset_password_request)

    async def api_get_identify_stars_job_result_post(self, api_get_identify_stars_job_result_post_request: ApiGetIdentifyStarsJobResultPostRequest) -> IdentifyStarsJobResult:
        return await api_get_identify_stars_job_result_post(api_get_identify_stars_job_result_post_request)

    async def api_get_profile_stats_post(self, profile_stats_request: any) -> ProfileStatsResponse:
        return await api_get_profile_stats_post_handler(profile_stats_request)

    async def api_create_blog_post(
        self,
        api_create_blog_post_request: ApiCreateBlogPostRequest,
    ) -> ApiCreateBlogPost200Response:
        return await api_create_blog_post(api_create_blog_post_request)

    async def api_delete_blog_post(
        self,
        blog_id: BlogID,
    ) -> BlogID:
        return await api_delete_blog_post(blog_id)

    async def api_like_blog_post(
        self,
        blog_id: BlogID,
    ) -> ApiLikeBlogPost200Response:
        return await api_like_blog_post(blog_id)

    async def api_list_saved_blogs_post(
        self,
        pagination_query: PaginationQuery,
    ) -> BlogsList:
        return await api_list_saved_blogs_post(pagination_query)

    async def api_list_star_blogs_post(
        self,
        api_list_star_blogs_post_request: ApiListStarBlogsPostRequest,
    ) -> BlogsList:
        return await api_list_star_blogs_post(api_list_star_blogs_post_request)

    async def api_list_user_blogs_post(
        self,
        pagination_query: PaginationQuery,
    ) -> BlogsList:
        payload = pagination_query.to_dict() if hasattr(
            pagination_query, "to_dict") else pagination_query
        return await api_list_user_blogs_post(payload)

    async def api_report_blog_post(
        self,
        api_report_blog_post_request: ApiReportBlogPostRequest,
    ) -> BlogID:
        return await api_report_blog_post(api_report_blog_post_request)

    async def api_save_blog_post(
        self,
        blog_id: BlogID,
    ) -> BlogID:
        return await api_save_blog_post(blog_id)

    async def api_view_blog_post(
        self,
        blog_id: BlogID,
    ) -> Blog:
        return await api_view_blog_post(blog_id)

    async def api_comment_blog_post(
        self,
        api_comment_blog_post_request: ApiCommentBlogPostRequest,
    ) -> ApiCommentBlogPost200Response:
        return await api_comment_blog_post(api_comment_blog_post_request)

    async def api_check_login_status_post(self) -> CommonMessage:
        return await api_check_login_status_post()

    async def api_create_star_message_post(
        self,
        star_message: StarMessage,
    ) -> CommonID:
        return await api_create_star_message_post_handler(star_message)

    async def api_get_star_message_post(
        self,
        common_id: CommonID,
    ) -> StarMessage:
        return await api_get_star_message_post_handler(common_id)

    async def api_health_get(self) -> None:
        return

    async def api_create_star_message_post(self, star_message: StarMessage) -> CommonID:
        return await api_create_star_message_post(star_message)

    async def api_get_star_message_post(self, common_id: CommonID) -> StarMessage:
        return await api_get_star_message_post(common_id)
