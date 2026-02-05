import pytest
from fastapi.testclient import TestClient

def setup_user(client: TestClient, username: str, password: str):
    """
    辅助函数：先注册一个用户，用于后续删除测试
    """
    client.post("/api/userReg", json={
        "username": username,
        "password": password,
        "email": f"{username}@example.com"
    })

def test_delete_user_success(client: TestClient):
    """
    测试：使用正确密码成功删除用户
    """
    username = "user_to_delete"
    password = "correct_password"
    
    # 1. 准备数据：先注册
    setup_user(client, username, password)

    # 2. 执行删除操作
    payload = {
        "username": username,
        "password": password
    }
    response = client.post("/api/deleteUser", json=payload)
    
    # 3. 验证删除接口返回成功
    assert response.status_code == 200
    # 注意：根据你的 handler 实现，这里可能是 message 或其他字段
    assert "successfully" in str(response.json())

    # 4. 关键验证：尝试再次登录，应该返回 404 (用户不存在)
    login_response = client.post("/api/userLogin", json={
        "username": username,
        "password": password
    })
    assert login_response.status_code == 404

def test_delete_user_wrong_password(client: TestClient):
    """
    测试：密码错误时，禁止删除用户
    """
    username = "safe_user"
    password = "my_secret_password"
    
    # 1. 准备数据
    setup_user(client, username, password)

    # 2. 尝试用错误密码删除
    payload = {
        "username": username,
        "password": "wrong_password_123"
    }
    response = client.post("/api/deleteUser", json=payload)
    
    # 3. 验证被拦截 (401 Unauthorized)
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"]

    # 4. 关键验证：用户依然存在 (登录应该成功)
    login_response = client.post("/api/userLogin", json={
        "username": username,
        "password": password
    })
    assert login_response.status_code == 200

def test_delete_user_not_found(client: TestClient):
    """
    测试：尝试删除一个不存在的用户
    """
    payload = {
        "username": "ghost_user_999",
        "password": "any_password"
    }
    response = client.post("/api/deleteUser", json=payload)
    
    # 验证返回 404 Not Found
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]