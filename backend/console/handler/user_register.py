import hashlib
from sqlalchemy import text

# ✅ 修正导入路径：配合 PYTHONPATH="gen/py/src;." 使用
# 这样能确保和生成的代码使用同一个类定义，避免类型冲突
from openapi_server.models.user_auth import UserAuth
from openapi_server.models.user_response import UserResponse

# 引入数据库连接
from backend.console.dal.rds.client import get_db

async def api_user_reg_post(user_auth: UserAuth) -> UserResponse:
    print(f"📝 收到注册请求: {user_auth.username} / {user_auth.email}")
    
    # 1. 简单校验
    if not user_auth.email:
        print("❌ 错误: 邮箱不能为空")
        # 实际项目中建议: raise HTTPException(status_code=400, detail="Email required")
    
    # 2. 密码加密 (SHA256)
    # UserAuth.password 是 SecretStr 类型，必须用 .get_secret_value() 获取明文
    raw_password = user_auth.password.get_secret_value()
    hashed_password = hashlib.sha256(raw_password.encode()).hexdigest()
    
    # 3. 写入数据库
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 编写 SQL (确保字段名与数据库 create_user.sql 一致)
        sql = text("""
            INSERT INTO user (username, password, email) 
            VALUES (:username, :password, :email)
        """)
        
        result = db.execute(sql, {
            "username": user_auth.username,
            "password": hashed_password,
            "email": user_auth.email
        })
        db.commit()
        
        # 4. 获取新生成的自增 ID
        new_user_id = result.lastrowid
        print(f"✅ 用户注册成功，ID: {new_user_id}")
        
        # 5. 返回结果 
        # 注意：API 定义 userID 是 String，数据库是 BigInt，必须 str() 转换
        return UserResponse(
            userID=str(new_user_id), 
            username=user_auth.username,
            email=user_auth.email
        )
        
    except Exception as e:
        db.rollback()
        print(f"❌ 数据库错误: {e}")
        # 这里抛出异常，FastAPI 会捕获并返回 500 Internal Server Error
        raise e
    finally:
        db.close()