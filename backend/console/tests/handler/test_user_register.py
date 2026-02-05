import pytest
from fastapi.testclient import TestClient

def test_register_success(client: TestClient):
    """Test successful user registration"""
    payload = {
        "username": "newuser",
        "password": "password123",
        "email": "new@example.com"
    }
    response = client.post("/api/userReg", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    
    # 修正：OpenAPI 定义 ID 为 String 类型，所以这里检查 str
    assert "userID" in data
    assert isinstance(data["userID"], str) 
    # 可选：检查它是否是数字字符串
    assert data["userID"].isdigit()

def test_register_duplicate_username(client: TestClient):
    """Test registration with existing username (Should fail)"""
    # 1. Register first user
    payload = {
        "username": "duplicate_user",
        "password": "password123",
        "email": "u1@example.com"
    }
    client.post("/api/userReg", json=payload)

    # 2. Try to register same username again
    payload_dup = {
        "username": "duplicate_user",
        "password": "password456",
        "email": "u2@example.com"
    }
    response = client.post("/api/userReg", json=payload_dup)
    
    # Expecting 400 Bad Request
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_register_missing_fields(client: TestClient):
    """Test registration with missing required fields"""
    # Missing password
    payload = {
        "username": "incomplete_user",
        "email": "fail@example.com"
    }
    response = client.post("/api/userReg", json=payload)
    
    # FastAPIs validation error is usually 422
    assert response.status_code == 422