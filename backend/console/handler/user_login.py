import hashlib
from fastapi import HTTPException
from gen.py.src.openapi_server.models.user_auth import UserAuth
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User
from backend.console.utils.auth import create_access_token


async def api_user_login_post(user_auth: UserAuth):
    print(f"Received login request: {user_auth.username}")

    db = next(get_db())

    # 1. Query user
    user = User.get_by_username(db, user_auth.username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Verify password
    pwd_raw = user_auth.password.get_secret_value()
    pwd_hash = hashlib.sha256(pwd_raw.encode()).hexdigest()

    if user.password != pwd_hash:
        print("Password verification failed")
        raise HTTPException(status_code=401, detail="Password incorrect")

    # 3. Generate JWT Token
    token_data = {
        "sub": user.username,
        "user_id": user.id
    }
    access_token = create_access_token(token_data)

    print(f"Login successful for user: {user.username}")
    return {"message": "Login successful", "token": access_token}
