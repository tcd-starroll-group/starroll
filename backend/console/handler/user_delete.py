import hashlib
from fastapi import HTTPException

from openapi_server.models.user_auth import UserAuth
from openapi_server.models.common_message import CommonMessage
from backend.console.dal.rds.client import db_context
from backend.console.dal.rds.user import User
from backend.console.utils.auth import get_current_user_id


async def api_delete_user_post(user_auth: UserAuth) -> CommonMessage:

    user_id = get_current_user_id()

    with db_context() as db:
        try:
            user = User.get_by_id(db, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            User.delete_by_id(db, user.id)
            print(f"User {user_auth.username} deleted successfully")
            return CommonMessage(message="Account deleted successfully")

        except Exception as e:
            db.rollback()
            if isinstance(e, HTTPException):
                raise e
            print(f"Delete user failed: {e}")
            raise HTTPException(
                status_code=500, detail="Internal Server Error")
