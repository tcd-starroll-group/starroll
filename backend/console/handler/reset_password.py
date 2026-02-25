import hashlib
from fastapi import HTTPException
from gen.py.src.openapi_server.models.reset_password_request import ResetPasswordRequest
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User
from backend.console.utils.verification_code import verification_code_store
from gen.py.src.openapi_server.models.api_change_password_post200_response import ApiChangePasswordPost200Response


async def api_reset_password_post(
    reset_password_request: ResetPasswordRequest,
) -> ApiChangePasswordPost200Response:
    print(f"Received password reset request for email: {reset_password_request.email}")

    db_gen = get_db()
    db = next(db_gen)
    try:
        # 1. Check email exists
        user = User.get_by_email(db, reset_password_request.email)
        if not user:
            raise HTTPException(status_code=404, detail="Email not found")

        # 2. Verify verification code
        is_valid = verification_code_store.verify_verification_code(
            reset_password_request.email, reset_password_request.code
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")

        # 3. Update password
        new_pwd = reset_password_request.new_password
        if hasattr(new_pwd, "get_secret_value"):
            new_pwd = new_pwd.get_secret_value()

        new_hash = hashlib.sha256(new_pwd.encode()).hexdigest()
        User.update_password_by_email(db, reset_password_request.email, new_hash)

       
        db.commit()
        
        print(f"Password reset successfully for email: {reset_password_request.email}")
        return {"message": "Password reset successfully"}

    except Exception as e:
        
        try:
            db.rollback()
        except Exception:
            pass  
        if isinstance(e, HTTPException):
            raise e
        print(f"Password reset failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        
        try:
            db_gen.close()
        except Exception:
            pass