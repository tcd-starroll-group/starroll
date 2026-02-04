import hashlib
from fastapi import HTTPException

from gen.py.src.openapi_server.models.user_auth import UserAuth
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User


async def api_delete_user_post(user_auth: UserAuth) -> dict:
    print(f"Received delete request: {user_auth.username}")

    db_gen = get_db()
    db = next(db_gen)

    try:
        # 1. Verify user exists
        sql_check = text(
            "SELECT password FROM user WHERE username = :username")
        result = db.execute(
            sql_check, {"username": user_auth.username}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Verify password (critical security step)
        # Stored password is hashed; hash input before comparison
        stored_password = result[0]
        input_password_raw = user_auth.password.get_secret_value()
        input_password_hash = hashlib.sha256(
            input_password_raw.encode()).hexdigest()

        if stored_password != input_password_hash:
            print(
                f"Password verification failed for user: {user_auth.username}")
            raise HTTPException(
                status_code=401, detail="Password incorrect, cannot delete account")

        # 3. Execute delete
        sql_delete = text("DELETE FROM user WHERE username = :username")
        db.execute(sql_delete, {"username": user_auth.username})
        db.commit()

        print(f"User {user_auth.username} deleted successfully")
        return {"message": "Account deleted successfully"}

    except Exception as e:
        db.rollback()
        # If already an HTTPException (e.g., wrong password), re-raise
        if isinstance(e, HTTPException):
            raise e
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        db.close()
