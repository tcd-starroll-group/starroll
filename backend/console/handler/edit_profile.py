import hashlib
from fastapi import HTTPException
from openapi_server.models.change_password_request import ChangePasswordRequest
from openapi_server.models.profile_and_token import ProfileAndToken

from backend.console.dal.rds.client import db_context
from backend.console.dal.rds.user import User
from backend.console.utils.auth import verify_access_token


async def api_edit_profile_post(profile_and_token: ProfileAndToken):
    print(f"Received change password request: {profile_and_token.username}")

    valid_token = profile_and_token.token
    # a=verify_access_token(user_with_token.token)
    valid_payload, is_valid = verify_access_token(valid_token)
    if is_valid:
        print(f"有效 Payload: {valid_payload}")
    else:
        print("Token 无效")
        raise HTTPException(status_code=404, detail="token invalid")

    with db_context() as db:
        # 1. Query user
        user_by_name = db.query(User).filter(
            User.username == profile_and_token.username).first()
        user = User.get_by_id(db, user_by_name.id) if user_by_name else None
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # User.update_password(db, profile_and_token.username, new_hash)
        User.edit_profile(db, user.id,
                          profile_and_token.profile)

        return {"message": "profile updated successfully"}
