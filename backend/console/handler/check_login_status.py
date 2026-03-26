from openapi_server.models.common_message import CommonMessage


async def api_check_login_status_post(
) -> CommonMessage:
    return CommonMessage(message="ok")
