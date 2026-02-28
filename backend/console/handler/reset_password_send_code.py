from fastapi import HTTPException,Body
from gen.py.src.openapi_server.models.reset_password_send_code_request import ResetPasswordSendCodeRequest
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User
from backend.console.utils.verification_code import verification_code_store
from backend.console.utils.email_sender import send_verification_email
from gen.py.src.openapi_server.models.api_change_password_post200_response import ApiChangePasswordPost200Response

async def api_reset_password_send_code_post(
    reset_password_send_code_request: ResetPasswordSendCodeRequest = Body(None, description=""),
) -> ApiChangePasswordPost200Response:
    print(f"Received forgot password request for email: {reset_password_send_code_request.email}")

    db_gen = get_db()
    db = next(db_gen)
    try:
        # 1. check email exist
        user = User.get_by_email(db, reset_password_send_code_request.email)
        if not user:
            raise HTTPException(status_code=404, detail="Email not found")
        if user.username != reset_password_send_code_request.user_name:
            raise HTTPException(status_code=400, detail="User not found")

        # 2. loading code
        code = verification_code_store.generate_verification_code()
        verification_code_store.save_verification_code(reset_password_send_code_request.email, code)

        # 3. send email
        success = send_verification_email(reset_password_send_code_request.email, code)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send verification email")

        print(f"Verification code sent to {reset_password_send_code_request.email}")
        return {"message": "Verification code sent successfully"}

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Send verification code failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        try:
            db_gen.close()
        except Exception:
            pass