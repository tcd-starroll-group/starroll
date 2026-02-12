import hashlib
from fastapi import HTTPException
from gen.py.src.openapi_server.models.change_password_request import ChangePasswordRequest
from gen.py.src.openapi_server.models.profile_and_token import ProfileAndToken

from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User




async def api_edit_profile_post(profile_and_token: ProfileAndToken):
    print(f"Received change password request: {profile_and_token.username}")

    db = next(get_db())
    try:
        # 1. Query user
        user = User.get_by_username(db, profile_and_token.username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        

        # User.update_password(db, profile_and_token.username, new_hash)
        User.edit_profile(db, profile_and_token.username, profile_and_token.profile)
        

        
        return {"message": "profile updated successfully"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        print(f"Change password failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
