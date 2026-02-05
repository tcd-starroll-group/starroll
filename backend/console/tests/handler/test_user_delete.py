import pytest
from fastapi.testclient import TestClient

def setup_user(client: TestClient, username: str, password: str):
    """
    Helper function: Register a user first to be used for subsequent deletion tests.
    """
    client.post("/api/userReg", json={
        "username": username,
        "password": password,
        "email": f"{username}@example.com"
    })

def test_delete_user_success(client: TestClient):
    """
    Test: Successfully delete a user using the correct password.
    """
    username = "user_to_delete"
    password = "correct_password"
    
    # 1. Prepare data: Perform registration first
    setup_user(client, username, password)

    # 2. Execute the deletion operation
    payload = {
        "username": username,
        "password": password
    }
    response = client.post("/api/deleteUser", json=payload)
    
    # 3. Verify the deletion endpoint returns success
    # Note: Depending on your handler implementation, the key might be 'message' or another field
    assert response.status_code == 200
    assert "successfully" in str(response.json())

    # 4. Critical Verification: Attempt to login again; should return 404 (User Not Found)
    login_response = client.post("/api/userLogin", json={
        "username": username,
        "password": password
    })
    assert login_response.status_code == 404

def test_delete_user_wrong_password(client: TestClient):
    """
    Test: Prohibit user deletion when the password is incorrect.
    """
    username = "safe_user"
    password = "my_secret_password"
    
    # 1. Prepare data
    setup_user(client, username, password)

    # 2. Attempt to delete with an incorrect password
    payload = {
        "username": username,
        "password": "wrong_password_123"
    }
    response = client.post("/api/deleteUser", json=payload)
    
    # 3. Verify the request is intercepted (401 Unauthorized)
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"]

    # 4. Critical Verification: User should still exist (Login should succeed)
    login_response = client.post("/api/userLogin", json={
        "username": username,
        "password": password
    })
    assert login_response.status_code == 200

def test_delete_user_not_found(client: TestClient):
    """
    Test: Attempt to delete a user that does not exist.
    """
    payload = {
        "username": "ghost_user_999",
        "password": "any_password"
    }
    response = client.post("/api/deleteUser", json=payload)
    
    # Verify it returns 404 Not Found
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]