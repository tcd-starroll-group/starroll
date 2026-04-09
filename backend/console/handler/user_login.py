import hashlib
from fastapi import HTTPException
from openapi_server.models.user_auth import UserAuth
from backend.console.dal.rds.client import db_context
from backend.console.dal.rds.user import User
from backend.console.utils.auth import create_access_token
from backend.model.auth import TokenData


async def api_user_login_post(user_auth: UserAuth):
    print(f"Received login request: {user_auth.username}")

    with db_context() as db:
        # 1. Query user
        user_by_name = db.query(User).filter(
            User.username == user_auth.username).first()
        user = User.get_by_id(db, user_by_name.id) if user_by_name else None

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Verify password
        pwd_raw = user_auth.password.get_secret_value()
        pwd_hash = hashlib.sha256(pwd_raw.encode()).hexdigest()

        if user.password != pwd_hash:
            print("Password verification failed")
            raise HTTPException(status_code=401, detail="Password incorrect")

        # 3. Generate JWT Token
        token_data = TokenData.from_user(user.username, user.id)
        access_token = create_access_token(token_data.model_dump())

        return {"message": "Login successful", "token": access_token, "userID": str(user.id)}
