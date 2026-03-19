from fastapi import HTTPException

<<<<<<< HEAD
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User
from backend.console.utils.auth import verify_access_token
from gen.py.src.openapi_server.models.api_update_last_gps_post_request import ApiUpdateLastGpsPostRequest


async def api_update_last_gps_post(
    update_last_gps_request: ApiUpdateLastGpsPostRequest,
):
    """Persist the latest user GPS for recommendation emails."""
    valid_payload, is_valid = verify_access_token(update_last_gps_request.token)
    if not is_valid:
        raise HTTPException(status_code=404, detail="token invalid")

    db = next(get_db())
    try:
        user = User.get_by_username(db, update_last_gps_request.username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        User.update_last_gps(
            db,
            update_last_gps_request.username,
            update_last_gps_request.gps.to_dict(),
        )
        return {"message": "last gps updated successfully"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        print(f"Update last gps failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
=======
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
>>>>>>> main
