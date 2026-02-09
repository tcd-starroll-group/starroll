# coding: utf-8

from fastapi.testclient import TestClient


from typing import Optional  # noqa: F401
from openapi_server.models.api_calculate_star_coordinates_post200_response import ApiCalculateStarCoordinatesPost200Response  # noqa: F401
from openapi_server.models.api_calculate_star_coordinates_post_request import ApiCalculateStarCoordinatesPostRequest  # noqa: F401
from openapi_server.models.api_check_room_status_post200_response import ApiCheckRoomStatusPost200Response  # noqa: F401
from openapi_server.models.api_check_room_status_post_request import ApiCheckRoomStatusPostRequest  # noqa: F401
from openapi_server.models.api_comment_blog_post200_response import ApiCommentBlogPost200Response  # noqa: F401
from openapi_server.models.api_comment_blog_post_request import ApiCommentBlogPostRequest  # noqa: F401
from openapi_server.models.api_create_blog_post200_response import ApiCreateBlogPost200Response  # noqa: F401
from openapi_server.models.api_create_blog_post_request import ApiCreateBlogPostRequest  # noqa: F401
from openapi_server.models.api_delete_blog_post200_response import ApiDeleteBlogPost200Response  # noqa: F401
from openapi_server.models.api_delete_comment_post_request import ApiDeleteCommentPostRequest  # noqa: F401
from openapi_server.models.api_display_chat_room_get200_response import ApiDisplayChatRoomGet200Response  # noqa: F401
from openapi_server.models.api_display_save_success_post200_response import ApiDisplaySaveSuccessPost200Response  # noqa: F401
from openapi_server.models.api_display_save_success_post_request import ApiDisplaySaveSuccessPostRequest  # noqa: F401
from openapi_server.models.api_display_star_details_post_request import ApiDisplayStarDetailsPostRequest  # noqa: F401
from openapi_server.models.api_display_starfield_post200_response import ApiDisplayStarfieldPost200Response  # noqa: F401
from openapi_server.models.api_display_starfield_post_request import ApiDisplayStarfieldPostRequest  # noqa: F401
from openapi_server.models.api_elimilate_errors_post200_response import ApiElimilateErrorsPost200Response  # noqa: F401
from openapi_server.models.api_elimilate_errors_post_request import ApiElimilateErrorsPostRequest  # noqa: F401
from openapi_server.models.api_exit_chat_room_post200_response import ApiExitChatRoomPost200Response  # noqa: F401
from openapi_server.models.api_exit_chat_room_post_request import ApiExitChatRoomPostRequest  # noqa: F401
from openapi_server.models.api_get_camera_data_post200_response import ApiGetCameraDataPost200Response  # noqa: F401
from openapi_server.models.api_get_chat_room_info_post200_response import ApiGetChatRoomInfoPost200Response  # noqa: F401
from openapi_server.models.api_get_chat_room_info_post_request import ApiGetChatRoomInfoPostRequest  # noqa: F401
from openapi_server.models.api_get_chat_room_post200_response import ApiGetChatRoomPost200Response  # noqa: F401
from openapi_server.models.api_get_chat_room_post_request import ApiGetChatRoomPostRequest  # noqa: F401
from openapi_server.models.api_get_message_post200_response import ApiGetMessagePost200Response  # noqa: F401
from openapi_server.models.api_get_message_post_request import ApiGetMessagePostRequest  # noqa: F401
from openapi_server.models.api_get_saved_blogs_post200_response import ApiGetSavedBlogsPost200Response  # noqa: F401
from openapi_server.models.api_get_saved_blogs_post_request import ApiGetSavedBlogsPostRequest  # noqa: F401
from openapi_server.models.api_get_star_catalog_post200_response import ApiGetStarCatalogPost200Response  # noqa: F401
from openapi_server.models.api_get_star_details_post_request import ApiGetStarDetailsPostRequest  # noqa: F401
from openapi_server.models.api_like_blog_post200_response import ApiLikeBlogPost200Response  # noqa: F401
from openapi_server.models.api_list_blogs_post200_response import ApiListBlogsPost200Response  # noqa: F401
from openapi_server.models.api_list_blogs_post_request import ApiListBlogsPostRequest  # noqa: F401
from openapi_server.models.api_request_accuracy_adjust_post200_response import ApiRequestAccuracyAdjustPost200Response  # noqa: F401
from openapi_server.models.api_request_accuracy_adjust_post_request import ApiRequestAccuracyAdjustPostRequest  # noqa: F401
from openapi_server.models.api_request_save_type_post200_response import ApiRequestSaveTypePost200Response  # noqa: F401
from openapi_server.models.api_request_stargazing_time_post200_response import ApiRequestStargazingTimePost200Response  # noqa: F401
from openapi_server.models.api_request_stargazing_time_post_request import ApiRequestStargazingTimePostRequest  # noqa: F401
from openapi_server.models.api_send_message_post200_response import ApiSendMessagePost200Response  # noqa: F401
from openapi_server.models.api_send_message_post_request import ApiSendMessagePostRequest  # noqa: F401
from openapi_server.models.api_set_user_post200_response import ApiSetUserPost200Response  # noqa: F401
from openapi_server.models.api_trigger_starfield_render_post200_response import ApiTriggerStarfieldRenderPost200Response  # noqa: F401
from openapi_server.models.api_trigger_starfield_render_post_request import ApiTriggerStarfieldRenderPostRequest  # noqa: F401
from openapi_server.models.api_username_verify_post200_response import ApiUsernameVerifyPost200Response  # noqa: F401
from openapi_server.models.api_username_verify_post_request import ApiUsernameVerifyPostRequest  # noqa: F401
from openapi_server.models.api_verify_user_token_post_request import ApiVerifyUserTokenPostRequest  # noqa: F401
from openapi_server.models.api_view_blog_post_request import ApiViewBlogPostRequest  # noqa: F401
from openapi_server.models.attitude import Attitude  # noqa: F401
from openapi_server.models.blog import Blog  # noqa: F401
from openapi_server.models.change_password_request import ChangePasswordRequest  # noqa: F401
from openapi_server.models.error_response import ErrorResponse  # noqa: F401
from openapi_server.models.gps import GPS  # noqa: F401
from openapi_server.models.star_details import StarDetails  # noqa: F401
from openapi_server.models.token_response import TokenResponse  # noqa: F401
from openapi_server.models.user_auth import UserAuth  # noqa: F401
from openapi_server.models.user_response import UserResponse  # noqa: F401


def test_api_display_chat_room_get(client: TestClient):
    """Test case for api_display_chat_room_get

    Display chat room entry button in GUI
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/displayChatRoom",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_exit_chat_room_post(client: TestClient):
    """Test case for api_exit_chat_room_post

    Exit chat room
    """
    api_exit_chat_room_post_request = openapi_server.ApiExitChatRoomPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/exitChatRoom",
    #    headers=headers,
    #    json=api_exit_chat_room_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_list_blogs_post(client: TestClient):
    """Test case for api_list_blogs_post

    List all blogs under the certain star
    """
    api_list_blogs_post_request = openapi_server.ApiListBlogsPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/listBlogs",
    #    headers=headers,
    #    json=api_list_blogs_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_view_blog_post(client: TestClient):
    """Test case for api_view_blog_post

    Details of one blog
    """
    api_view_blog_post_request = openapi_server.ApiViewBlogPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/viewBlog",
    #    headers=headers,
    #    json=api_view_blog_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_create_blog_post(client: TestClient):
    """Test case for api_create_blog_post

    Create a new blog
    """
    api_create_blog_post_request = openapi_server.ApiCreateBlogPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/createBlog",
    #    headers=headers,
    #    json=api_create_blog_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_get_saved_blogs_post(client: TestClient):
    """Test case for api_get_saved_blogs_post

    List the blogs user saved
    """
    api_get_saved_blogs_post_request = openapi_server.ApiGetSavedBlogsPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/getSavedBlogs",
    #    headers=headers,
    #    json=api_get_saved_blogs_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_get_location_post(client: TestClient):
    """Test case for api_get_location_post

    Get current location
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/getLocation",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_get_attitude_post(client: TestClient):
    """Test case for api_get_attitude_post

    Get attitude of the mobile device
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/getAttitude",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_get_camera_data_post(client: TestClient):
    """Test case for api_get_camera_data_post

    Get camera data
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/getCameraData",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_get_star_catalog_post(client: TestClient):
    """Test case for api_get_star_catalog_post

    Get star catalog
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/getStarCatalog",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_calculate_star_coordinates_post(client: TestClient):
    """Test case for api_calculate_star_coordinates_post

    calculate star coordinates
    """
    api_calculate_star_coordinates_post_request = openapi_server.ApiCalculateStarCoordinatesPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/calculateStarCoordinates",
    #    headers=headers,
    #    json=api_calculate_star_coordinates_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_trigger_starfield_render_post(client: TestClient):
    """Test case for api_trigger_starfield_render_post

    Trigger starfield rendering
    """
    api_trigger_starfield_render_post_request = openapi_server.ApiTriggerStarfieldRenderPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/triggerStarfieldRender",
    #    headers=headers,
    #    json=api_trigger_starfield_render_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_request_stargazing_time_post(client: TestClient):
    """Test case for api_request_stargazing_time_post

    Request optimal stargazing time
    """
    api_request_stargazing_time_post_request = openapi_server.ApiRequestStargazingTimePostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/requestStargazingTime",
    #    headers=headers,
    #    json=api_request_stargazing_time_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_request_accuracy_adjust_post(client: TestClient):
    """Test case for api_request_accuracy_adjust_post

    Request accuracy adjustment
    """
    api_request_accuracy_adjust_post_request = openapi_server.ApiRequestAccuracyAdjustPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/requestAccuracyAdjust",
    #    headers=headers,
    #    json=api_request_accuracy_adjust_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_display_starfield_post(client: TestClient):
    """Test case for api_display_starfield_post

    Display starfield
    """
    api_display_starfield_post_request = openapi_server.ApiDisplayStarfieldPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/displayStarfield",
    #    headers=headers,
    #    json=api_display_starfield_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_display_star_details_post(client: TestClient):
    """Test case for api_display_star_details_post

    Display star details
    """
    api_display_star_details_post_request = openapi_server.ApiDisplayStarDetailsPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/displayStarDetails",
    #    headers=headers,
    #    json=api_display_star_details_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_request_save_type_post(client: TestClient):
    """Test case for api_request_save_type_post

    Request save type options
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/requestSaveType",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_display_save_success_post(client: TestClient):
    """Test case for api_display_save_success_post

    Display save success confirmation
    """
    api_display_save_success_post_request = openapi_server.ApiDisplaySaveSuccessPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/displaySaveSuccess",
    #    headers=headers,
    #    json=api_display_save_success_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_elimilate_errors_post(client: TestClient):
    """Test case for api_elimilate_errors_post

    Eliminating the errors between the stars' positions that we calculated and the stars' positions captured by the camera. These errors are generally caused by the limited accuracy of the sensor.
    """
    api_elimilate_errors_post_request = openapi_server.ApiElimilateErrorsPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/elimilateErrors",
    #    headers=headers,
    #    json=api_elimilate_errors_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_get_chat_room_post(client: TestClient):
    """Test case for api_get_chat_room_post

    Join the chat room
    """
    api_get_chat_room_post_request = openapi_server.ApiGetChatRoomPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/getChatRoom",
    #    headers=headers,
    #    json=api_get_chat_room_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_get_chat_room_info_post(client: TestClient):
    """Test case for api_get_chat_room_info_post

    Retrieve chat room from social system
    """
    api_get_chat_room_info_post_request = openapi_server.ApiGetChatRoomInfoPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/getChatRoomInfo",
    #    headers=headers,
    #    json=api_get_chat_room_info_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_get_message_post(client: TestClient):
    """Test case for api_get_message_post

    Retrieve chat room messages
    """
    api_get_message_post_request = openapi_server.ApiGetMessagePostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/getMessage",
    #    headers=headers,
    #    json=api_get_message_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_send_message_post(client: TestClient):
    """Test case for api_send_message_post

    Send message to chat room
    """
    api_send_message_post_request = openapi_server.ApiSendMessagePostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/sendMessage",
    #    headers=headers,
    #    json=api_send_message_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_get_star_details_post(client: TestClient):
    """Test case for api_get_star_details_post

    calculate star details
    """
    api_get_star_details_post_request = openapi_server.ApiGetStarDetailsPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/getStarDetails",
    #    headers=headers,
    #    json=api_get_star_details_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_check_room_status_post(client: TestClient):
    """Test case for api_check_room_status_post

    Check chat room status
    """
    api_check_room_status_post_request = openapi_server.ApiCheckRoomStatusPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/checkRoomStatus",
    #    headers=headers,
    #    json=api_check_room_status_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_set_user_post(client: TestClient):
    """Test case for api_set_user_post

    Set/modify username and password
    """
    change_password_request = {"password0":"OldPa$$w0rd","password1":"NewStr0ngPa$$w0rd!","username":"user123"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/setUser",
    #    headers=headers,
    #    json=change_password_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_user_login_post(client: TestClient):
    """Test case for api_user_login_post

    User login
    """
    user_auth = {"password":"Str0ngPa$$w0rd!","username":"user123"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/userLogin",
    #    headers=headers,
    #    json=user_auth,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_user_reg_post(client: TestClient):
    """Test case for api_user_reg_post

    User register
    """
    user_auth = {"password":"Str0ngPa$$w0rd!","username":"user123"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/userReg",
    #    headers=headers,
    #    json=user_auth,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_username_verify_post(client: TestClient):
    """Test case for api_username_verify_post

    Verify the username
    """
    api_username_verify_post_request = openapi_server.ApiUsernameVerifyPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/usernameVerify",
    #    headers=headers,
    #    json=api_username_verify_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_verify_user_token_post(client: TestClient):
    """Test case for api_verify_user_token_post

    Verify the user's Token
    """
    api_verify_user_token_post_request = openapi_server.ApiVerifyUserTokenPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/verifyUserToken",
    #    headers=headers,
    #    json=api_verify_user_token_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_delete_blog_post(client: TestClient):
    """Test case for api_delete_blog_post

    Delete a blog
    """
    api_get_saved_blogs_post_request = openapi_server.ApiGetSavedBlogsPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/deleteBlog",
    #    headers=headers,
    #    json=api_get_saved_blogs_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_like_blog_post(client: TestClient):
    """Test case for api_like_blog_post

    Like a blog
    """
    api_get_saved_blogs_post_request = openapi_server.ApiGetSavedBlogsPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/likeBlog",
    #    headers=headers,
    #    json=api_get_saved_blogs_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_comment_blog_post(client: TestClient):
    """Test case for api_comment_blog_post

    Comment a blog
    """
    api_comment_blog_post_request = openapi_server.ApiCommentBlogPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/commentBlog",
    #    headers=headers,
    #    json=api_comment_blog_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_delete_comment_post(client: TestClient):
    """Test case for api_delete_comment_post

    Delete a comment
    """
    api_delete_comment_post_request = openapi_server.ApiDeleteCommentPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/deleteComment",
    #    headers=headers,
    #    json=api_delete_comment_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_save_blog_post(client: TestClient):
    """Test case for api_save_blog_post

    Save a blog
    """
    api_get_saved_blogs_post_request = openapi_server.ApiGetSavedBlogsPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/saveBlog",
    #    headers=headers,
    #    json=api_get_saved_blogs_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_api_report_blog_post(client: TestClient):
    """Test case for api_report_blog_post

    Report a blog
    """
    api_get_saved_blogs_post_request = openapi_server.ApiGetSavedBlogsPostRequest()

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/reportBlog",
    #    headers=headers,
    #    json=api_get_saved_blogs_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

