import hashlib
from sqlalchemy import text
from fastapi import HTTPException

from gen.py.src.openapi_server.models.user_auth import UserAuth
from backend.console.dal.rds.client import get_db


async def api_delete_user_post(user_auth: UserAuth) -> dict:
    print(f"⚠️ 收到注销请求: {user_auth.username}")

    db_gen = get_db()
    db = next(db_gen)

    try:
        # 1. 验证用户是否存在
        sql_check = text(
            "SELECT password FROM user WHERE username = :username")
        result = db.execute(
            sql_check, {"username": user_auth.username}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 2. 验证密码 (核心安全步骤)
        # 数据库里的密码是哈希过的，所以要把输入的密码也哈希一下进行比对
        stored_password = result[0]
        input_password_raw = user_auth.password.get_secret_value()
        input_password_hash = hashlib.sha256(
            input_password_raw.encode()).hexdigest()

        if stored_password != input_password_hash:
            print(f"❌ 用户 {user_auth.username} 密码验证失败")
            raise HTTPException(status_code=401, detail="密码错误，无法注销")

        # 3. 执行删除
        sql_delete = text("DELETE FROM user WHERE username = :username")
        db.execute(sql_delete, {"username": user_auth.username})
        db.commit()

        print(f"✅ 用户 {user_auth.username} 已成功注销")
        return {"message": "账号已成功注销"}

    except Exception as e:
        db.rollback()
        # 如果已经是 HTTPException (比如密码错误)，直接抛出
        if isinstance(e, HTTPException):
            raise e
        print(f"❌ 数据库错误: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")
    finally:
        db.close()
