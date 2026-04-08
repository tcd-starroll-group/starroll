import logging
from fastapi import Body, HTTPException
from openapi_server.models.api_discover_star_post_request import ApiDiscoverStarPostRequest
from openapi_server.models.common_message import CommonMessage
from backend.console.dal.rds.user_discovered_stars import UserDiscoveredStars
from backend.console.dal.rds.client import db_context
import backend.console.utils.auth as auth_module

logger = logging.getLogger(__name__)


async def api_discover_star_post(
    api_discover_star_post_request: ApiDiscoverStarPostRequest = Body(
        None, description=""),
) -> CommonMessage:
    if not api_discover_star_post_request or api_discover_star_post_request.hip is None:
        raise HTTPException(status_code=400, detail="hip is required")

    user_id = auth_module.get_current_user_id()
    hip_id = api_discover_star_post_request.hip

    with db_context() as db:
        if not UserDiscoveredStars.exists(db, user_id=int(user_id), hip_id=int(hip_id)):
            UserDiscoveredStars.create(
                db, user_id=int(user_id), hip_id=int(hip_id))

    return CommonMessage(message="ok")
