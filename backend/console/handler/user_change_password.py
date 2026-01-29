import hashlib
from sqlalchemy import text
from fastapi import HTTPException
from openapi_server.models.change_password_request import ChangePasswordRequest
from backend.console.dal.rds.client import get_db

async def api_change_password_post(request: ChangePasswordRequest) -> dict:
    print(f"🔐 收到修改密码请求: {request.username}")

    db_gen = get_db()
    db = next(db_gen)

    try:
        # 1. 查找用户
        sql_check = text("SELECT password FROM user WHERE username = :username")
        result = db.execute(sql_check, {"username": request.username}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="用户不存在")

        stored_password_hash = result[0]

        # 2. 验证旧密码 (处理 SecretStr)
        # 使用 .get_secret_value() 转换
        old_pwd_raw = request.old_password
        if hasattr(old_pwd_raw, "get_secret_value"):
            old_pwd_raw = old_pwd_raw.get_secret_value()
            
        input_old_hash = hashlib.sha256(old_pwd_raw.encode()).hexdigest()

        if stored_password_hash != input_old_hash:
            raise HTTPException(status_code=401, detail="旧密码错误")

        # 3. 处理新密码并更新
        new_pwd_raw = request.new_password
        if hasattr(new_pwd_raw, "get_secret_value"):
            new_pwd_raw = new_pwd_raw.get_secret_value()
            
        new_password_hash = hashlib.sha256(new_pwd_raw.encode()).hexdigest()

        sql_update = text("UPDATE user SET password = :new_password WHERE username = :username")
        db.execute(sql_update, {
            "new_password": new_password_hash,
            "username": request.username
        })
        db.commit()

        return {"message": "密码修改成功"}

    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException): raise e
        print(f"❌ 错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()