from fastapi import HTTPException

from backend.console.dal.rds.client import db_context
from backend.console.dal.rds.user import User
from backend.console.utils.auth import verify_access_token
from openapi_server.models.update_last_gps_request import UpdateLastGpsRequest
from backend.console.utils.auth import get_current_user_id


async def api_update_last_gps_post(
    update_last_gps_request: UpdateLastGpsRequest,
):
    """Persist the latest user GPS for recommendation emails."""

    with db_context() as db:
        user = User.get_by_id(db, get_current_user_id())
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.set_last_gps(db, update_last_gps_request.gps.to_dict())
        return {"message": "last gps updated successfully"}
