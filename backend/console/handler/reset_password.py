import hashlib
from fastapi import HTTPException,Body
from gen.py.src.openapi_server.models.reset_password_request import ResetPasswordRequest
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User
from backend.console.utils.verification_code import verification_code_store
from gen.py.src.openapi_server.models.api_change_password_post200_response import ApiChangePasswordPost200Response

async def api_reset_password_post(
    reset_password_request: ResetPasswordRequest = Body(None, description=""),
) -> ApiChangePasswordPost200Response:
    print(f"Received password reset request for email: {ResetPasswordRequest.email}")

    db = next(get_db())
    try:
        # 1. check email exist
        user = User.get_by_email(db,  ResetPasswordRequest.email)
        if not user:
            raise HTTPException(status_code=404, detail="Email not found")
        if user.username !=  ResetPasswordRequest.user_name:
             raise HTTPException(status_code=400, detail="User not found")

        # 2. verificy password exist
        is_valid = verification_code_store.verify_verification_code( ResetPasswordRequest.email, ResetPasswordRequest.code)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")

        # 3. renew password
        new_pwd = ResetPasswordRequest.new_password
        if hasattr(new_pwd, "get_secret_value"):
            new_pwd = new_pwd.get_secret_value()

        new_hash = hashlib.sha256(new_pwd.encode()).hexdigest()
        User.update_password_by_email(db, ResetPasswordRequest.email, new_hash)

        print(f"Password reset successfully for email: {ResetPasswordRequest.email}")
        return {"message": "Password reset successfully"}

    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        print(f"Password reset failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")