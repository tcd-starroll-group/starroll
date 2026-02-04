import hashlib
from fastapi import HTTPException
from openapi_server.models.user_auth import UserAuth
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User

async def api_delete_user_post(user_auth: UserAuth) -> dict:
    print(f"Received delete user request: {user_auth.username}")
    
    db = next(get_db())

    try:
        # 1. Query user
        user = User.get_by_username(db, user_auth.username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Verify password
        input_pwd = user_auth.password.get_secret_value()
        input_hash = hashlib.sha256(input_pwd.encode()).hexdigest()

        if user.password != input_hash:
            raise HTTPException(status_code=401, detail="Password incorrect")

        # 3. Delete user
        User.delete_by_username(db, user_auth.username)
        
        print(f"User {user_auth.username} deleted successfully")
        return {"message": "Account deleted successfully"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        print(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")