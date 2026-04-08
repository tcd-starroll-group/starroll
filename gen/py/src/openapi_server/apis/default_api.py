# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.default_api_base import BaseDefaultApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from typing import Any, Dict
from openapi_server.models.api_calculate_star_coordinates_post200_response import ApiCalculateStarCoordinatesPost200Response
from openapi_server.models.api_calculate_star_coordinates_post_request import ApiCalculateStarCoordinatesPostRequest
from openapi_server.models.api_check_room_status_post200_response import ApiCheckRoomStatusPost200Response
from openapi_server.models.api_check_room_status_post_request import ApiCheckRoomStatusPostRequest
from openapi_server.models.api_comment_blog_post200_response import ApiCommentBlogPost200Response
from openapi_server.models.api_comment_blog_post_request import ApiCommentBlogPostRequest
from openapi_server.models.api_create_blog_post200_response import ApiCreateBlogPost200Response
from openapi_server.models.api_create_blog_post_request import ApiCreateBlogPostRequest
from openapi_server.models.api_create_identify_stars_job_post200_response import ApiCreateIdentifyStarsJobPost200Response
from openapi_server.models.api_create_identify_stars_job_post_request import ApiCreateIdentifyStarsJobPostRequest
from openapi_server.models.api_delete_comment_post_request import ApiDeleteCommentPostRequest
from openapi_server.models.api_discover_star_post_request import ApiDiscoverStarPostRequest
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
from openapi_server.models.api_get_identify_stars_job_result_post_request import ApiGetIdentifyStarsJobResultPostRequest
from openapi_server.models.api_get_message_post200_response import ApiGetMessagePost200Response
from openapi_server.models.api_get_message_post_request import ApiGetMessagePostRequest
from openapi_server.models.api_get_star_catalog_post200_response import ApiGetStarCatalogPost200Response
from openapi_server.models.api_get_star_details_post_request import ApiGetStarDetailsPostRequest
from openapi_server.models.api_like_blog_post200_response import ApiLikeBlogPost200Response
from openapi_server.models.api_list_identify_stars_jobs_post200_response import ApiListIdentifyStarsJobsPost200Response
from openapi_server.models.api_list_star_blogs_post_request import ApiListStarBlogsPostRequest
from openapi_server.models.api_report_blog_post_request import ApiReportBlogPostRequest
from openapi_server.models.api_request_accuracy_adjust_post200_response import ApiRequestAccuracyAdjustPost200Response
from openapi_server.models.api_request_accuracy_adjust_post_request import ApiRequestAccuracyAdjustPostRequest
from openapi_server.models.api_request_save_type_post200_response import ApiRequestSaveTypePost200Response
from openapi_server.models.api_request_stargazing_time_post200_response import ApiRequestStargazingTimePost200Response
from openapi_server.models.api_request_stargazing_time_post_request import ApiRequestStargazingTimePostRequest
from openapi_server.models.api_send_message_post200_response import ApiSendMessagePost200Response
from openapi_server.models.api_send_message_post_request import ApiSendMessagePostRequest
from openapi_server.models.api_trigger_starfield_render_post200_response import ApiTriggerStarfieldRenderPost200Response
from openapi_server.models.api_trigger_starfield_render_post_request import ApiTriggerStarfieldRenderPostRequest
from openapi_server.models.api_user_reg_post_request import ApiUserRegPostRequest
from openapi_server.models.api_username_verify_post_request import ApiUsernameVerifyPostRequest
from openapi_server.models.attitude import Attitude
from openapi_server.models.blog import Blog
from openapi_server.models.blog_id import BlogID
from openapi_server.models.blogs_list import BlogsList
from openapi_server.models.change_password_request import ChangePasswordRequest
from openapi_server.models.common_id import CommonID
from openapi_server.models.common_message import CommonMessage
from openapi_server.models.error_response import ErrorResponse
from openapi_server.models.gps import GPS
from openapi_server.models.identify_stars_job_result import IdentifyStarsJobResult
from openapi_server.models.pagination_query import PaginationQuery
from openapi_server.models.profile_and_token import ProfileAndToken
from openapi_server.models.profile_stats_response import ProfileStatsResponse
from openapi_server.models.reset_password_request import ResetPasswordRequest
from openapi_server.models.reset_password_send_code_request import ResetPasswordSendCodeRequest
from openapi_server.models.star_details import StarDetails
from openapi_server.models.star_message import StarMessage
from openapi_server.models.token_response import TokenResponse
from openapi_server.models.update_last_gps_request import UpdateLastGpsRequest
from openapi_server.models.user_auth import UserAuth
from openapi_server.models.user_response import UserResponse


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/api/displayChatRoom",
    responses={
        200: {"model": ApiDisplayChatRoomGet200Response, "description": "Button configuration retrieved successfully"},
    },
    tags=["default"],
    summary="Display chat room entry button in GUI",
    response_model_by_alias=True,
)
async def api_display_chat_room_get(
) -> ApiDisplayChatRoomGet200Response:
    """Returns data to render chat room entry button in the graphical interface"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_display_chat_room_get()


@router.post(
    "/api/exitChatRoom",
    responses={
        200: {"model": ApiExitChatRoomPost200Response, "description": "Successfully exited chat room"},
    },
    tags=["default"],
    summary="Exit chat room",
    response_model_by_alias=True,
)
async def api_exit_chat_room_post(
    api_exit_chat_room_post_request: ApiExitChatRoomPostRequest = Body(None, description=""),
) -> ApiExitChatRoomPost200Response:
    """Updates user&#39;s participation status and triggers related notifications"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_exit_chat_room_post(api_exit_chat_room_post_request)


@router.post(
    "/api/listUserBlogs",
    responses={
        200: {"model": BlogsList, "description": "OK"},
    },
    tags=["default"],
    summary="List all blogs posted by a specific user",
    response_model_by_alias=True,
)
async def api_list_user_blogs_post(
    pagination_query: PaginationQuery = Body(None, description=""),
) -> BlogsList:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_list_user_blogs_post(pagination_query)


@router.post(
    "/api/listStarBlogs",
    responses={
        200: {"model": BlogsList, "description": "OK"},
    },
    tags=["default"],
    summary="List all blogs under the certain star",
    response_model_by_alias=True,
)
async def api_list_star_blogs_post(
    api_list_star_blogs_post_request: ApiListStarBlogsPostRequest = Body(None, description=""),
) -> BlogsList:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_list_star_blogs_post(api_list_star_blogs_post_request)


@router.post(
    "/api/viewBlog",
    responses={
        200: {"model": Blog, "description": "OK"},
    },
    tags=["default"],
    summary="Details of one blog",
    response_model_by_alias=True,
)
async def api_view_blog_post(
    blog_id: BlogID = Body(None, description=""),
) -> Blog:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_view_blog_post(blog_id)


@router.post(
    "/api/createBlog",
    responses={
        200: {"model": ApiCreateBlogPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Create a new blog",
    response_model_by_alias=True,
)
async def api_create_blog_post(
    api_create_blog_post_request: ApiCreateBlogPostRequest = Body(None, description=""),
) -> ApiCreateBlogPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_create_blog_post(api_create_blog_post_request)


@router.post(
    "/api/listSavedBlogs",
    responses={
        200: {"model": BlogsList, "description": "OK"},
    },
    tags=["default"],
    summary="List all blogs saved by the user",
    response_model_by_alias=True,
)
async def api_list_saved_blogs_post(
    pagination_query: PaginationQuery = Body(None, description=""),
) -> BlogsList:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_list_saved_blogs_post(pagination_query)


@router.post(
    "/api/getLocation",
    responses={
        200: {"model": GPS, "description": "OK"},
    },
    tags=["default"],
    summary="Get current location",
    response_model_by_alias=True,
)
async def api_get_location_post(
) -> GPS:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_location_post()


@router.post(
    "/api/getAttitude",
    responses={
        200: {"model": Attitude, "description": "OK"},
    },
    tags=["default"],
    summary="Get attitude of the mobile device",
    response_model_by_alias=True,
)
async def api_get_attitude_post(
) -> Attitude:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_attitude_post()


@router.post(
    "/api/getCameraData",
    responses={
        200: {"model": ApiGetCameraDataPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Get camera data",
    response_model_by_alias=True,
)
async def api_get_camera_data_post(
) -> ApiGetCameraDataPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_camera_data_post()


@router.post(
    "/api/getStarCatalog",
    responses={
        200: {"model": ApiGetStarCatalogPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Get star catalog",
    response_model_by_alias=True,
)
async def api_get_star_catalog_post(
) -> ApiGetStarCatalogPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_star_catalog_post()


@router.post(
    "/api/calculateStarCoordinates",
    responses={
        200: {"model": ApiCalculateStarCoordinatesPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="calculate star coordinates",
    response_model_by_alias=True,
)
async def api_calculate_star_coordinates_post(
    api_calculate_star_coordinates_post_request: ApiCalculateStarCoordinatesPostRequest = Body(None, description=""),
) -> ApiCalculateStarCoordinatesPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_calculate_star_coordinates_post(api_calculate_star_coordinates_post_request)


@router.post(
    "/api/triggerStarfieldRender",
    responses={
        200: {"model": ApiTriggerStarfieldRenderPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Trigger starfield rendering",
    response_model_by_alias=True,
)
async def api_trigger_starfield_render_post(
    api_trigger_starfield_render_post_request: ApiTriggerStarfieldRenderPostRequest = Body(None, description=""),
) -> ApiTriggerStarfieldRenderPost200Response:
    """Initiate starfield rendering process using corrected star coordinates and camera parameters"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_trigger_starfield_render_post(api_trigger_starfield_render_post_request)


@router.post(
    "/api/requestStargazingTime",
    responses={
        200: {"model": ApiRequestStargazingTimePost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Request optimal stargazing time",
    response_model_by_alias=True,
)
async def api_request_stargazing_time_post(
    api_request_stargazing_time_post_request: ApiRequestStargazingTimePostRequest = Body(None, description=""),
) -> ApiRequestStargazingTimePost200Response:
    """Get recommended stargazing time range based on GPS location"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_request_stargazing_time_post(api_request_stargazing_time_post_request)


@router.post(
    "/api/requestAccuracyAdjust",
    responses={
        200: {"model": ApiRequestAccuracyAdjustPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Request accuracy adjustment",
    response_model_by_alias=True,
)
async def api_request_accuracy_adjust_post(
    api_request_accuracy_adjust_post_request: ApiRequestAccuracyAdjustPostRequest = Body(None, description=""),
) -> ApiRequestAccuracyAdjustPost200Response:
    """Adjust calculation accuracy for star coordinates based on sensor precision"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_request_accuracy_adjust_post(api_request_accuracy_adjust_post_request)


@router.post(
    "/api/displayStarfield",
    responses={
        200: {"model": ApiDisplayStarfieldPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Display starfield",
    response_model_by_alias=True,
)
async def api_display_starfield_post(
    api_display_starfield_post_request: ApiDisplayStarfieldPostRequest = Body(None, description=""),
) -> ApiDisplayStarfieldPost200Response:
    """Retrieve rendered starfield data for GUI display"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_display_starfield_post(api_display_starfield_post_request)


@router.post(
    "/api/displayStarDetails",
    responses={
        200: {"model": StarDetails, "description": "OK"},
    },
    tags=["default"],
    summary="Display star details",
    response_model_by_alias=True,
)
async def api_display_star_details_post(
    api_display_star_details_post_request: ApiDisplayStarDetailsPostRequest = Body(None, description=""),
) -> StarDetails:
    """Retrieve detailed astronomical information of a specific star"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_display_star_details_post(api_display_star_details_post_request)


@router.post(
    "/api/requestSaveType",
    responses={
        200: {"model": ApiRequestSaveTypePost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Request save type options",
    response_model_by_alias=True,
)
async def api_request_save_type_post(
) -> ApiRequestSaveTypePost200Response:
    """Get available save types for rendered starfield"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_request_save_type_post()


@router.post(
    "/api/displaySaveSuccess",
    responses={
        200: {"model": ApiDisplaySaveSuccessPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Display save success confirmation",
    response_model_by_alias=True,
)
async def api_display_save_success_post(
    api_display_save_success_post_request: ApiDisplaySaveSuccessPostRequest = Body(None, description=""),
) -> ApiDisplaySaveSuccessPost200Response:
    """Return save result and metadata after starfield is saved"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_display_save_success_post(api_display_save_success_post_request)


@router.post(
    "/api/createIdentifyStarsJob",
    responses={
        200: {"model": ApiCreateIdentifyStarsJobPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Create a job to identify the stars in the image.",
    response_model_by_alias=True,
)
async def api_create_identify_stars_job_post(
    api_create_identify_stars_job_post_request: ApiCreateIdentifyStarsJobPostRequest = Body(None, description=""),
) -> ApiCreateIdentifyStarsJobPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_create_identify_stars_job_post(api_create_identify_stars_job_post_request)


@router.post(
    "/api/listIdentifyStarsJobs",
    responses={
        200: {"model": ApiListIdentifyStarsJobsPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="List identify stars jobs.",
    response_model_by_alias=True,
)
async def api_list_identify_stars_jobs_post(
    pagination_query: PaginationQuery = Body(None, description=""),
) -> ApiListIdentifyStarsJobsPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_list_identify_stars_jobs_post(pagination_query)


@router.post(
    "/api/getIdentifyStarsJobResult",
    responses={
        200: {"model": IdentifyStarsJobResult, "description": "OK"},
    },
    tags=["default"],
    summary="get identify stars job result.",
    response_model_by_alias=True,
)
async def api_get_identify_stars_job_result_post(
    api_get_identify_stars_job_result_post_request: ApiGetIdentifyStarsJobResultPostRequest = Body(None, description=""),
) -> IdentifyStarsJobResult:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_identify_stars_job_result_post(api_get_identify_stars_job_result_post_request)


@router.post(
    "/api/elimilateErrors",
    responses={
        200: {"model": ApiElimilateErrorsPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Eliminating the errors between the stars&#39; positions that we calculated and the stars&#39; positions captured by the camera. These errors are generally caused by the limited accuracy of the sensor.",
    response_model_by_alias=True,
)
async def api_elimilate_errors_post(
    api_elimilate_errors_post_request: ApiElimilateErrorsPostRequest = Body(None, description=""),
) -> ApiElimilateErrorsPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_elimilate_errors_post(api_elimilate_errors_post_request)


@router.post(
    "/api/getChatRoom",
    responses={
        200: {"model": ApiGetChatRoomPost200Response, "description": "Successfully entered the chat room"},
    },
    tags=["default"],
    summary="Join the chat room",
    response_model_by_alias=True,
)
async def api_get_chat_room_post(
    api_get_chat_room_post_request: ApiGetChatRoomPostRequest = Body(None, description=""),
) -> ApiGetChatRoomPost200Response:
    """Join the chat room"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_chat_room_post(api_get_chat_room_post_request)


@router.post(
    "/api/getChatRoomInfo",
    responses={
        200: {"model": ApiGetChatRoomInfoPost200Response, "description": "Chat room information retrieved successfully"},
    },
    tags=["default"],
    summary="Retrieve chat room from social system",
    response_model_by_alias=True,
)
async def api_get_chat_room_info_post(
    api_get_chat_room_info_post_request: ApiGetChatRoomInfoPostRequest = Body(None, description=""),
) -> ApiGetChatRoomInfoPost200Response:
    """Gets specified chat room information from the social system"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_chat_room_info_post(api_get_chat_room_info_post_request)


@router.post(
    "/api/getMessage",
    responses={
        200: {"model": ApiGetMessagePost200Response, "description": "Messages retrieved successfully"},
    },
    tags=["default"],
    summary="Retrieve chat room messages",
    response_model_by_alias=True,
)
async def api_get_message_post(
    api_get_message_post_request: ApiGetMessagePostRequest = Body(None, description=""),
) -> ApiGetMessagePost200Response:
    """Gets historical and real-time messages from the chat room"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_message_post(api_get_message_post_request)


@router.post(
    "/api/sendMessage",
    responses={
        200: {"model": ApiSendMessagePost200Response, "description": "Message sent successfully"},
    },
    tags=["default"],
    summary="Send message to chat room",
    response_model_by_alias=True,
)
async def api_send_message_post(
    api_send_message_post_request: ApiSendMessagePostRequest = Body(None, description=""),
) -> ApiSendMessagePost200Response:
    """Sends a message to the specified chat room for real-time communication"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_send_message_post(api_send_message_post_request)


@router.post(
    "/api/getStarDetails",
    responses={
        200: {"model": StarDetails, "description": "OK"},
    },
    tags=["default"],
    summary="calculate star details",
    response_model_by_alias=True,
)
async def api_get_star_details_post(
    api_get_star_details_post_request: ApiGetStarDetailsPostRequest = Body(None, description=""),
) -> StarDetails:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_star_details_post(api_get_star_details_post_request)


@router.post(
    "/api/checkRoomStatus",
    responses={
        200: {"model": ApiCheckRoomStatusPost200Response, "description": "Room status retrieved successfully"},
    },
    tags=["default"],
    summary="Check chat room status",
    response_model_by_alias=True,
)
async def api_check_room_status_post(
    api_check_room_status_post_request: ApiCheckRoomStatusPostRequest = Body(None, description=""),
) -> ApiCheckRoomStatusPost200Response:
    """Determines if a user can join the specified chat room"""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_check_room_status_post(api_check_room_status_post_request)


@router.post(
    "/api/setUser",
    responses={
        200: {"model": CommonMessage, "description": "Modify password successful."},
        400: {"model": ErrorResponse, "description": "Invalid request: For example, the new password does not meet the security requirements, or the new and old passwords are the same."},
        401: {"model": ErrorResponse, "description": "Unauthorized: Current password (password0) is incorrect"},
        404: {"model": ErrorResponse, "description": "Not Found: The username does not exist."},
    },
    tags=["default"],
    summary="Set/modify username and password",
    response_model_by_alias=True,
)
async def api_set_user_post(
    change_password_request: ChangePasswordRequest = Body(None, description=""),
) -> CommonMessage:
    """Modify the username and password by the username, current password(password0)and new password(password1) user provided."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_set_user_post(change_password_request)


@router.post(
    "/api/userLogin",
    responses={
        200: {"model": TokenResponse, "description": "Login successful."},
        401: {"model": ErrorResponse, "description": "Unauthorized: Incorrect username or password."},
    },
    tags=["default"],
    summary="User login",
    response_model_by_alias=True,
)
async def api_user_login_post(
    user_auth: UserAuth = Body(None, description=""),
) -> TokenResponse:
    """Use username and password to authentication, return a token if success."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_user_login_post(user_auth)


@router.post(
    "/api/editProfile",
    responses={
        200: {"model": UserResponse, "description": "Profile updated successfully."},
        400: {"model": ErrorResponse, "description": "Invalid request: For example, invalid JSON format."},
        401: {"model": ErrorResponse, "description": "Unauthorized: Authentication required."},
        404: {"model": ErrorResponse, "description": "User not found."},
    },
    tags=["default"],
    summary=" update user profile",
    response_model_by_alias=True,
)
async def api_edit_profile_post(
    profile_and_token: ProfileAndToken = Body(None, description=""),
) -> UserResponse:
    """update the user&#39;s profile information stored as JSON."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_edit_profile_post(profile_and_token)


@router.post(
    "/api/updateLastGps",
    responses={
        200: {"model": CommonMessage, "description": "Last GPS updated successfully."},
        401: {"model": ErrorResponse, "description": "Unauthorized: Authentication required."},
        404: {"model": ErrorResponse, "description": "User not found."},
    },
    tags=["default"],
    summary="update user last gps",
    response_model_by_alias=True,
)
async def api_update_last_gps_post(
    update_last_gps_request: UpdateLastGpsRequest = Body(None, description=""),
) -> CommonMessage:
    """update the user&#39;s latest GPS location used by recommendation emails."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_update_last_gps_post(update_last_gps_request)


@router.post(
    "/api/userReg",
    responses={
        201: {"model": UserResponse, "description": "Create user successful."},
        400: {"model": ErrorResponse, "description": "Invalid request: For example, the password does not meet the requirements."},
        409: {"model": ErrorResponse, "description": "Conflict: The username is already in use."},
    },
    tags=["default"],
    summary="User register",
    response_model_by_alias=True,
)
async def api_user_reg_post(
    api_user_reg_post_request: ApiUserRegPostRequest = Body(None, description=""),
) -> UserResponse:
    """Create an account with a new username and password."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_user_reg_post(api_user_reg_post_request)


@router.post(
    "/api/changePassword",
    responses={
        200: {"model": CommonMessage, "description": "Password updated successfully"},
        401: {"description": "Old password incorrect"},
        404: {"description": "User not found"},
    },
    tags=["default"],
    response_model_by_alias=True,
)
async def api_change_password_post(
    change_password_request: ChangePasswordRequest = Body(None, description=""),
) -> CommonMessage:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_change_password_post(change_password_request)


@router.post(
    "/api/resetPasswordSendCode",
    responses={
        200: {"model": CommonMessage, "description": "Verification code sent successfully"},
        404: {"description": "Email not found"},
        500: {"description": "Failed to send email"},
    },
    tags=["default"],
    summary="send code to email",
    response_model_by_alias=True,
)
async def api_reset_password_send_code_post(
    reset_password_send_code_request: ResetPasswordSendCodeRequest = Body(None, description=""),
) -> CommonMessage:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_reset_password_send_code_post(reset_password_send_code_request)


@router.post(
    "/api/resetPassword",
    responses={
        200: {"model": CommonMessage, "description": "Password reset successfully"},
        400: {"description": "Invalid or expired verification code"},
        404: {"description": "Email not found"},
    },
    tags=["default"],
    summary="Use code to reset password",
    response_model_by_alias=True,
)
async def api_reset_password_post(
    reset_password_request: ResetPasswordRequest = Body(None, description=""),
) -> CommonMessage:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_reset_password_post(reset_password_request)


@router.post(
    "/api/deleteUser",
    responses={
        200: {"model": CommonMessage, "description": "Deletion successful"},
        401: {"description": "Password incorrect"},
        404: {"description": "User not found"},
    },
    tags=["default"],
    summary="注销账号",
    response_model_by_alias=True,
)
async def api_delete_user_post(
    user_auth: UserAuth = Body(None, description=""),
) -> CommonMessage:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_delete_user_post(user_auth)


@router.post(
    "/api/usernameVerify",
    responses={
        200: {"model": CommonMessage, "description": "Username available"},
        409: {"model": ErrorResponse, "description": "The username is already in use."},
    },
    tags=["default"],
    summary="Verify the username",
    response_model_by_alias=True,
)
async def api_username_verify_post(
    api_username_verify_post_request: ApiUsernameVerifyPostRequest = Body(None, description=""),
) -> CommonMessage:
    """Check whether the username is available."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_username_verify_post(api_username_verify_post_request)


@router.post(
    "/api/verifyUserToken",
    responses={
        200: {"model": UserResponse, "description": "Token is valid."},
        401: {"model": ErrorResponse, "description": "Invalid or expired Token."},
    },
    tags=["default"],
    summary="Verify the user&#39;s Token",
    response_model_by_alias=True,
)
async def api_verify_user_token_post(
) -> UserResponse:
    """Check whether the provided Token is valid. If it is valid, return the corresponding user information."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_verify_user_token_post()


@router.post(
    "/api/deleteBlog",
    responses={
        200: {"model": BlogID, "description": "OK"},
    },
    tags=["default"],
    summary="Delete a blog",
    response_model_by_alias=True,
)
async def api_delete_blog_post(
    blog_id: BlogID = Body(None, description=""),
) -> BlogID:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_delete_blog_post(blog_id)


@router.post(
    "/api/likeBlog",
    responses={
        200: {"model": ApiLikeBlogPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Like a blog",
    response_model_by_alias=True,
)
async def api_like_blog_post(
    blog_id: BlogID = Body(None, description=""),
) -> ApiLikeBlogPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_like_blog_post(blog_id)


@router.post(
    "/api/commentBlog",
    responses={
        200: {"model": ApiCommentBlogPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Comment a blog",
    response_model_by_alias=True,
)
async def api_comment_blog_post(
    api_comment_blog_post_request: ApiCommentBlogPostRequest = Body(None, description=""),
) -> ApiCommentBlogPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_comment_blog_post(api_comment_blog_post_request)


@router.post(
    "/api/deleteComment",
    responses={
        200: {"model": ApiCommentBlogPost200Response, "description": "OK"},
    },
    tags=["default"],
    summary="Delete a comment",
    response_model_by_alias=True,
)
async def api_delete_comment_post(
    api_delete_comment_post_request: ApiDeleteCommentPostRequest = Body(None, description=""),
) -> ApiCommentBlogPost200Response:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_delete_comment_post(api_delete_comment_post_request)


@router.post(
    "/api/saveBlog",
    responses={
        200: {"model": BlogID, "description": "OK"},
    },
    tags=["default"],
    summary="Save a blog",
    response_model_by_alias=True,
)
async def api_save_blog_post(
    blog_id: BlogID = Body(None, description=""),
) -> BlogID:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_save_blog_post(blog_id)


@router.post(
    "/api/reportBlog",
    responses={
        200: {"model": BlogID, "description": "OK"},
    },
    tags=["default"],
    summary="Report a blog",
    response_model_by_alias=True,
)
async def api_report_blog_post(
    api_report_blog_post_request: ApiReportBlogPostRequest = Body(None, description=""),
) -> BlogID:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_report_blog_post(api_report_blog_post_request)


@router.post(
    "/api/getProfileStats",
    responses={
        200: {"model": ProfileStatsResponse, "description": "OK"},
    },
    tags=["default"],
    summary="Get user profile stats",
    response_model_by_alias=True,
)
async def api_get_profile_stats_post(
    body: Dict[str, Any] = Body(None, description=""),
) -> ProfileStatsResponse:
    """Retrieve the user&#39;s scanning statistics, rank, and join date for the profile view."""
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_profile_stats_post(body)


@router.post(
    "/api/checkLoginStatus",
    responses={
        200: {"model": CommonMessage, "description": "OK"},
    },
    tags=["default"],
    summary="Get user profile stats",
    response_model_by_alias=True,
)
async def api_check_login_status_post(
) -> CommonMessage:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_check_login_status_post()


@router.post(
    "/api/createStarMessage",
    responses={
        200: {"model": CommonID, "description": "OK"},
    },
    tags=["default"],
    response_model_by_alias=True,
)
async def api_create_star_message_post(
    star_message: StarMessage = Body(None, description=""),
) -> CommonID:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_create_star_message_post(star_message)


@router.post(
    "/api/getStarMessage",
    responses={
        200: {"model": StarMessage, "description": "OK"},
    },
    tags=["default"],
    response_model_by_alias=True,
)
async def api_get_star_message_post(
    common_id: CommonID = Body(None, description=""),
) -> StarMessage:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_get_star_message_post(common_id)


@router.post(
    "/api/discoverStar",
    responses={
        200: {"model": CommonMessage, "description": "OK"},
    },
    tags=["default"],
    response_model_by_alias=True,
)
async def api_discover_star_post(
    api_discover_star_post_request: ApiDiscoverStarPostRequest = Body(None, description=""),
) -> CommonMessage:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_discover_star_post(api_discover_star_post_request)


@router.get(
    "/api/health",
    responses={
        200: {"description": "OK"},
    },
    tags=["default"],
    summary="health check",
    response_model_by_alias=True,
)
async def api_health_get(
) -> None:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().api_health_get()
