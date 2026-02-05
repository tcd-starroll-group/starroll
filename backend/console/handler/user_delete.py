import hashlib
from fastapi import HTTPException

# 导入 Pydantic 模型
from gen.py.src.openapi_server.models.user_auth import UserAuth
from gen.py.src.openapi_server.models.api_delete_user_post200_response import ApiDeleteUserPost200Response

# 导入数据库会话和 DAO
from backend.console.dal.rds.client import get_db
from backend.console.dal.rds.user import User

async def api_delete_user_post(user_auth: UserAuth) -> ApiDeleteUserPost200Response:
    """
    Handle user deletion request.
    Validates password before deletion.
    """
    print(f"Received delete user request: {user_auth.username}")
    
    db = next(get_db())

    try:
        # 1. 查询用户 (使用 DAO，严禁写 SQL)
        user = User.get_by_username(db, user_auth.username)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. 验证密码
        # 关键修正：因为 UserAuth 中 password 是 SecretStr，必须用 .get_secret_value()
        input_pwd_raw = user_auth.password.get_secret_value()
        input_hash = hashlib.sha256(input_pwd_raw.encode()).hexdigest()

        if user.password != input_hash:
            print(f"Delete failed: Password incorrect for user {user_auth.username}")
            raise HTTPException(status_code=401, detail="Password incorrect")

        # 3. 执行删除 (使用 DAO)
        User.delete_by_username(db, user_auth.username)
        
        print(f"User {user_auth.username} deleted successfully")
        
        # 4. 返回符合 OpenAPI 定义的对象
        return ApiDeleteUserPost200Response(message="Account deleted successfully")

    except Exception as e:
        db.rollback()
        # 如果已经是 HTTPException (比如密码错误)，直接抛出
        if isinstance(e, HTTPException):
            raise e
        
        # 记录其他未知错误
        print(f"Delete failed due to internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")