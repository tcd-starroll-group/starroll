# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictBytes, StrictStr
from typing import Any, Optional, Tuple, Union
from typing_extensions import Annotated
from openapi_server.models.api_calculate_star_coordinates_post200_response import ApiCalculateStarCoordinatesPost200Response
from openapi_server.models.api_calculate_star_coordinates_post_request import ApiCalculateStarCoordinatesPostRequest
from openapi_server.models.api_change_password_post200_response import ApiChangePasswordPost200Response
from openapi_server.models.api_check_room_status_post200_response import ApiCheckRoomStatusPost200Response
from openapi_server.models.api_check_room_status_post_request import ApiCheckRoomStatusPostRequest
from openapi_server.models.api_comment_blog_post200_response import ApiCommentBlogPost200Response
from openapi_server.models.api_comment_blog_post_request import ApiCommentBlogPostRequest
from openapi_server.models.api_create_blog_post200_response import ApiCreateBlogPost200Response
from openapi_server.models.api_create_blog_post_request import ApiCreateBlogPostRequest
from openapi_server.models.api_create_identify_stars_job_post200_response import ApiCreateIdentifyStarsJobPost200Response
from openapi_server.models.api_delete_blog_post200_response import ApiDeleteBlogPost200Response
from openapi_server.models.api_delete_comment_post_request import ApiDeleteCommentPostRequest
from openapi_server.models.api_display_chat_room_get200_response import ApiDisplayChatRoomGet200Response
from openapi_server.models.api_display_save_success_post200_response import ApiDisplaySaveSuccessPost200Response
from openapi_server.models.api_display_save_success_post_request import ApiDisplaySaveSuccessPostRequest
from openapi_server.models.api_display_star_details_post_request import ApiDisplayStarDetailsPostRequest
from openapi_server.models.api_display_starfield_post200_response import ApiDisplayStarfieldPost200Response
from openapi_server.models.api_display_starfield_post_request import ApiDisplayStarfieldPostRequest
from openapi_server.models.api_elimilate_errors_post200_response import ApiElimilateErrorsPost200Response
from openapi_server.models.api_elimilate_errors_post_request import ApiElimilateErrorsPostRequest
from openapi_server.models.api_exit_chat_room_post200_response import ApiExitChatRoomPost200Response
from openapi_server.models.api_exit_chat_room_post_request import ApiExitChatRoomPostRequest
from openapi_server.models.api_get_camera_data_post200_response import ApiGetCameraDataPost200Response
from openapi_server.models.api_get_chat_room_info_post200_response import ApiGetChatRoomInfoPost200Response
from openapi_server.models.api_get_chat_room_info_post_request import ApiGetChatRoomInfoPostRequest
from openapi_server.models.api_get_chat_room_post200_response import ApiGetChatRoomPost200Response
from openapi_server.models.api_get_chat_room_post_request import ApiGetChatRoomPostRequest
from openapi_server.models.api_get_identify_stars_job_result_post200_response import ApiGetIdentifyStarsJobResultPost200Response
from openapi_server.models.api_get_identify_stars_job_result_post_request import ApiGetIdentifyStarsJobResultPostRequest
from openapi_server.models.api_get_message_post200_response import ApiGetMessagePost200Response
from openapi_server.models.api_get_message_post_request import ApiGetMessagePostRequest
from openapi_server.models.api_get_saved_blogs_post200_response import ApiGetSavedBlogsPost200Response
from openapi_server.models.api_get_saved_blogs_post_request import ApiGetSavedBlogsPostRequest
from openapi_server.models.api_get_star_catalog_post200_response import ApiGetStarCatalogPost200Response
from openapi_server.models.api_get_star_details_post_request import ApiGetStarDetailsPostRequest
from openapi_server.models.api_like_blog_post200_response import ApiLikeBlogPost200Response
from openapi_server.models.api_list_blogs_post200_response import ApiListBlogsPost200Response
from openapi_server.models.api_list_blogs_post_request import ApiListBlogsPostRequest
from openapi_server.models.api_list_identify_stars_jobs_post200_response import ApiListIdentifyStarsJobsPost200Response
from openapi_server.models.api_list_identify_stars_jobs_post_request import ApiListIdentifyStarsJobsPostRequest
from openapi_server.models.api_request_accuracy_adjust_post200_response import ApiRequestAccuracyAdjustPost200Response
from openapi_server.models.api_request_accuracy_adjust_post_request import ApiRequestAccuracyAdjustPostRequest
from openapi_server.models.api_request_save_type_post200_response import ApiRequestSaveTypePost200Response
from openapi_server.models.api_request_stargazing_time_post200_response import ApiRequestStargazingTimePost200Response
from openapi_server.models.api_request_stargazing_time_post_request import ApiRequestStargazingTimePostRequest
from openapi_server.models.api_send_message_post200_response import ApiSendMessagePost200Response
from openapi_server.models.api_send_message_post_request import ApiSendMessagePostRequest
from openapi_server.models.api_set_user_post200_response import ApiSetUserPost200Response
from openapi_server.models.api_trigger_starfield_render_post200_response import ApiTriggerStarfieldRenderPost200Response
from openapi_server.models.api_trigger_starfield_render_post_request import ApiTriggerStarfieldRenderPostRequest
from openapi_server.models.api_user_reg_post_request import ApiUserRegPostRequest
from openapi_server.models.api_username_verify_post200_response import ApiUsernameVerifyPost200Response
from openapi_server.models.api_username_verify_post_request import ApiUsernameVerifyPostRequest
from openapi_server.models.api_verify_user_token_post_request import ApiVerifyUserTokenPostRequest
from openapi_server.models.api_view_blog_post_request import ApiViewBlogPostRequest
from openapi_server.models.attitude import Attitude
from openapi_server.models.blog import Blog
from openapi_server.models.change_password_request import ChangePasswordRequest
from openapi_server.models.error_response import ErrorResponse
from openapi_server.models.gps import GPS
from openapi_server.models.star_details import StarDetails
from openapi_server.models.token_response import TokenResponse
from openapi_server.models.user_auth import UserAuth
from openapi_server.models.user_credentials import UserCredentials
from openapi_server.models.user_response import UserResponse


class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def api_display_chat_room_get(
        self,
    ) -> ApiDisplayChatRoomGet200Response:
        """Returns data to render chat room entry button in the graphical interface"""
        ...


    async def api_exit_chat_room_post(
        self,
        api_exit_chat_room_post_request: ApiExitChatRoomPostRequest,
    ) -> ApiExitChatRoomPost200Response:
        """Updates user&#39;s participation status and triggers related notifications"""
        ...


    async def api_list_blogs_post(
        self,
        api_list_blogs_post_request: Optional[ApiListBlogsPostRequest],
    ) -> ApiListBlogsPost200Response:
        ...


    async def api_view_blog_post(
        self,
        api_view_blog_post_request: Optional[ApiViewBlogPostRequest],
    ) -> Blog:
        ...


    async def api_create_blog_post(
        self,
        api_create_blog_post_request: Optional[ApiCreateBlogPostRequest],
    ) -> ApiCreateBlogPost200Response:
        ...


    async def api_get_saved_blogs_post(
        self,
        api_get_saved_blogs_post_request: Optional[ApiGetSavedBlogsPostRequest],
    ) -> ApiGetSavedBlogsPost200Response:
        ...


    async def api_get_location_post(
        self,
    ) -> GPS:
        ...


    async def api_get_attitude_post(
        self,
    ) -> Attitude:
        ...


    async def api_get_camera_data_post(
        self,
    ) -> ApiGetCameraDataPost200Response:
        ...


    async def api_get_star_catalog_post(
        self,
    ) -> ApiGetStarCatalogPost200Response:
        ...


    async def api_calculate_star_coordinates_post(
        self,
        api_calculate_star_coordinates_post_request: Optional[ApiCalculateStarCoordinatesPostRequest],
    ) -> ApiCalculateStarCoordinatesPost200Response:
        ...


    async def api_trigger_starfield_render_post(
        self,
        api_trigger_starfield_render_post_request: Optional[ApiTriggerStarfieldRenderPostRequest],
    ) -> ApiTriggerStarfieldRenderPost200Response:
        """Initiate starfield rendering process using corrected star coordinates and camera parameters"""
        ...


    async def api_request_stargazing_time_post(
        self,
        api_request_stargazing_time_post_request: Optional[ApiRequestStargazingTimePostRequest],
    ) -> ApiRequestStargazingTimePost200Response:
        """Get recommended stargazing time range based on GPS location"""
        ...


    async def api_request_accuracy_adjust_post(
        self,
        api_request_accuracy_adjust_post_request: Optional[ApiRequestAccuracyAdjustPostRequest],
    ) -> ApiRequestAccuracyAdjustPost200Response:
        """Adjust calculation accuracy for star coordinates based on sensor precision"""
        ...


    async def api_display_starfield_post(
        self,
        api_display_starfield_post_request: Optional[ApiDisplayStarfieldPostRequest],
    ) -> ApiDisplayStarfieldPost200Response:
        """Retrieve rendered starfield data for GUI display"""
        ...


    async def api_display_star_details_post(
        self,
        api_display_star_details_post_request: Optional[ApiDisplayStarDetailsPostRequest],
    ) -> StarDetails:
        """Retrieve detailed astronomical information of a specific star"""
        ...


    async def api_request_save_type_post(
        self,
    ) -> ApiRequestSaveTypePost200Response:
        """Get available save types for rendered starfield"""
        ...


    async def api_display_save_success_post(
        self,
        api_display_save_success_post_request: Optional[ApiDisplaySaveSuccessPostRequest],
    ) -> ApiDisplaySaveSuccessPost200Response:
        """Return save result and metadata after starfield is saved"""
        ...


    async def api_create_identify_stars_job_post(
        self,
        image: Annotated[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]], Field(description="Image file to identify stars (JPEG, PNG, etc.)")],
        user_credentials: Optional[UserCredentials],
    ) -> ApiCreateIdentifyStarsJobPost200Response:
        ...


    async def api_list_identify_stars_jobs_post(
        self,
        api_list_identify_stars_jobs_post_request: Optional[ApiListIdentifyStarsJobsPostRequest],
    ) -> ApiListIdentifyStarsJobsPost200Response:
        ...


    async def api_get_identify_stars_job_result_post(
        self,
        api_get_identify_stars_job_result_post_request: ApiGetIdentifyStarsJobResultPostRequest,
    ) -> ApiGetIdentifyStarsJobResultPost200Response:
        ...


    async def api_elimilate_errors_post(
        self,
        api_elimilate_errors_post_request: Optional[ApiElimilateErrorsPostRequest],
    ) -> ApiElimilateErrorsPost200Response:
        ...


    async def api_get_chat_room_post(
        self,
        api_get_chat_room_post_request: ApiGetChatRoomPostRequest,
    ) -> ApiGetChatRoomPost200Response:
        """Join the chat room"""
        ...


    async def api_get_chat_room_info_post(
        self,
        api_get_chat_room_info_post_request: Optional[ApiGetChatRoomInfoPostRequest],
    ) -> ApiGetChatRoomInfoPost200Response:
        """Gets specified chat room information from the social system"""
        ...


    async def api_get_message_post(
        self,
        api_get_message_post_request: ApiGetMessagePostRequest,
    ) -> ApiGetMessagePost200Response:
        """Gets historical and real-time messages from the chat room"""
        ...


    async def api_send_message_post(
        self,
        api_send_message_post_request: ApiSendMessagePostRequest,
    ) -> ApiSendMessagePost200Response:
        """Sends a message to the specified chat room for real-time communication"""
        ...


    async def api_get_star_details_post(
        self,
        api_get_star_details_post_request: Optional[ApiGetStarDetailsPostRequest],
    ) -> StarDetails:
        ...


    async def api_check_room_status_post(
        self,
        api_check_room_status_post_request: Optional[ApiCheckRoomStatusPostRequest],
    ) -> ApiCheckRoomStatusPost200Response:
        """Determines if a user can join the specified chat room"""
        ...


    async def api_set_user_post(
        self,
        change_password_request: ChangePasswordRequest,
    ) -> ApiSetUserPost200Response:
        """Modify the username and password by the username, current password(password0)and new password(password1) user provided."""
        ...


    async def api_user_login_post(
        self,
        user_auth: UserAuth,
    ) -> TokenResponse:
        """Use username and password to authentication, return a token if success."""
        ...


    async def api_user_reg_post(
        self,
        api_user_reg_post_request: ApiUserRegPostRequest,
    ) -> UserResponse:
        """Create an account with a new username and password."""
        ...


    async def api_change_password_post(
        self,
        change_password_request: ChangePasswordRequest,
    ) -> ApiChangePasswordPost200Response:
        ...


    async def api_delete_user_post(
        self,
        user_auth: UserAuth,
    ) -> ApiChangePasswordPost200Response:
        ...


    async def api_username_verify_post(
        self,
        api_username_verify_post_request: ApiUsernameVerifyPostRequest,
    ) -> ApiUsernameVerifyPost200Response:
        """Check whether the username is available."""
        ...


    async def api_verify_user_token_post(
        self,
        api_verify_user_token_post_request: ApiVerifyUserTokenPostRequest,
    ) -> UserResponse:
        """Check whether the provided Token is valid. If it is valid, return the corresponding user information."""
        ...


    async def api_delete_blog_post(
        self,
        api_get_saved_blogs_post_request: Optional[ApiGetSavedBlogsPostRequest],
    ) -> ApiDeleteBlogPost200Response:
        ...


    async def api_like_blog_post(
        self,
        api_get_saved_blogs_post_request: Optional[ApiGetSavedBlogsPostRequest],
    ) -> ApiLikeBlogPost200Response:
        ...


    async def api_comment_blog_post(
        self,
        api_comment_blog_post_request: Optional[ApiCommentBlogPostRequest],
    ) -> ApiCommentBlogPost200Response:
        ...


    async def api_delete_comment_post(
        self,
        api_delete_comment_post_request: Optional[ApiDeleteCommentPostRequest],
    ) -> ApiCommentBlogPost200Response:
        ...


    async def api_save_blog_post(
        self,
        api_get_saved_blogs_post_request: Optional[ApiGetSavedBlogsPostRequest],
    ) -> ApiDeleteBlogPost200Response:
        ...


    async def api_report_blog_post(
        self,
        api_get_saved_blogs_post_request: Optional[ApiGetSavedBlogsPostRequest],
    ) -> ApiDeleteBlogPost200Response:
        ...
