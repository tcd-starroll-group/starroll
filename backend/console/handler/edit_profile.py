import hashlib
from fastapi import HTTPException
from openapi_server.models.change_password_request import ChangePasswordRequest
from openapi_server.models.profile_and_token import ProfileAndToken

from backend.console.dal.rds.client import db_context
from backend.console.dal.rds.user import User
from backend.console.utils.auth import verify_access_token


async def api_edit_profile_post(profile_and_token: ProfileAndToken):
    print(f"Received edit profile request: {profile_and_token.username}")

    valid_token = profile_and_token.token
    valid_payload, is_valid = verify_access_token(valid_token)
    
    if is_valid:
        print(f"Payload Valid: {valid_payload}")
    else:
        raise HTTPException(status_code=401, detail="token invalid")

    with db_context() as db:
        # 1. Query user securely
        token_username = valid_payload.get("sub")
        user_by_name = db.query(User).filter(User.username == token_username).first()
        user = User.get_by_id(db, user_by_name.id) if user_by_name else None
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. BULLETPROOF EXTRACTION: Convert the incoming profile payload to a real dictionary
        raw_profile = profile_and_token.profile or {}
        if isinstance(raw_profile, dict):
            new_data = dict(raw_profile)
        elif hasattr(raw_profile, "to_dict"):
            new_data = raw_profile.to_dict()
        elif hasattr(raw_profile, "dict"):
            new_data = raw_profile.dict(exclude_unset=True)
        else:
            new_data = vars(raw_profile) if hasattr(raw_profile, "__dict__") else {}

        # 3. Save Email to the explicit column and remove it from the dict
        if "email" in new_data:
            user.email = new_data.pop("email")

        # 4. Save Avatar to the explicit column and remove it from the dict
        if "avatar" in new_data:
            user.avatar_url = new_data.pop("avatar")

        # 5. Merge remaining data. Using dict() prevents SQLAlchemy JSON mutation bugs
        current_profile = dict(user.profile) if user.profile else {}
        updated_profile = {**current_profile, **new_data}
        
        # Save the JSON and commit the explicit column changes
        User.edit_profile(db, user.id, updated_profile)
        db.commit()

        return {"message": "profile updated successfully"}