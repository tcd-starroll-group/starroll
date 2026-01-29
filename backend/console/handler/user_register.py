import hashlib
from fastapi import HTTPException
from openapi_server.models.api_user_reg_post_request import ApiUserRegPostRequest
from openapi_server.models.user_response import UserResponse
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User

async def api_user_reg_post(user_auth: ApiUserRegPostRequest) -> UserResponse:
    print(f"Received registration request: {user_auth.username}")
    
    db = next(get_db())
    try:
        # 1. Check if username exists
        if User.get_by_username(db, user_auth.username):
            raise HTTPException(status_code=400, detail="Username already exists")

        # 2. Hash password
        pwd_raw = user_auth.password.get_secret_value()
        pwd_hash = hashlib.sha256(pwd_raw.encode()).hexdigest()

        # 3. Create user
        new_user = User.create(db, user_auth.username, pwd_hash, user_auth.email)

        print(f"User registered successfully, ID: {new_user.id}")
        return UserResponse(
            userID=str(new_user.id),
            username=new_user.username,
            email=new_user.email
        )
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")