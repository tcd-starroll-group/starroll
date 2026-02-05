import hashlib
from fastapi import HTTPException

from gen.py.src.openapi_server.models.user_auth import UserAuth
from gen.py.src.openapi_server.models.api_delete_user_post200_response import ApiDeleteUserPost200Response
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User


async def api_delete_user_post(user_auth: UserAuth) -> ApiDeleteUserPost200Response:
    print(f"Received delete user request: {user_auth.username}")

    db = next(get_db())
    try:
        # 1. Check if user exists
        user = User.get_by_username(db, user_auth.username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Verify password
        pwd_raw = user_auth.password
        if hasattr(pwd_raw, "get_secret_value"):
            pwd_raw = pwd_raw.get_secret_value()

        pwd_hash = hashlib.sha256(pwd_raw.encode()).hexdigest()

        if user.password != pwd_hash:
            print(f"Delete failed: Password incorrect for user {user_auth.username}")
            raise HTTPException(status_code=401, detail="Password incorrect")

        # 3. Delete user
        User.delete_by_username(db, user_auth.username)

        print(f"User {user_auth.username} deleted successfully")
        return ApiDeleteUserPost200Response(message="Account deleted successfully")

    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        print(f"Delete user failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")