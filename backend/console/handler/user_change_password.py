import hashlib
from fastapi import HTTPException
from gen.py.src.openapi_server.models.change_password_request import ChangePasswordRequest
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User


async def api_change_password_post(request: ChangePasswordRequest):
    print(f"Received change password request: {request.username}")

    db = next(get_db())
    try:
        # 1. Query user
        user = User.get_by_username(db, request.username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Verify old password
        old_pwd = request.old_password
        if hasattr(old_pwd, "get_secret_value"):
            old_pwd = old_pwd.get_secret_value()

        if user.password != hashlib.sha256(old_pwd.encode()).hexdigest():
            print("Old password incorrect")
            raise HTTPException(
                status_code=401, detail="Old password incorrect")

        # 3. Update new password
        new_pwd = request.new_password
        if hasattr(new_pwd, "get_secret_value"):
            new_pwd = new_pwd.get_secret_value()

        new_hash = hashlib.sha256(new_pwd.encode()).hexdigest()

        User.update_password(db, request.username, new_hash)

        print(f"User {request.username} password changed successfully")
        return {"message": "Password updated successfully"}
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        print(f"Change password failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
