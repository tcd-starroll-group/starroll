import pytest
from fastapi.testclient import TestClient

# Helper function to setup a user
def create_test_user(client, username="change_pwd_user", password="old_password"):
    client.post("/api/userReg", json={
        "username": username,
        "password": password,
        "email": f"{username}@example.com"
    })

def test_change_password_success(client: TestClient):
    """Test successful password change"""
    username = "cp_success"
    old_pass = "old_pass_123"
    new_pass = "new_pass_456"
    
    create_test_user(client, username, old_pass)

    # Change Password Request
    payload = {
        "username": username,
        "old_password": old_pass,
        "new_password": new_pass
    }
    # Note: If your API requires Token in headers, add headers=... here
    # Assuming standard flow based on previous docs
    response = client.post("/api/changePassword", json=payload)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

    # Verify: Login with OLD password should FAIL
    login_old = client.post("/api/userLogin", json={"username": username, "password": old_pass})
    assert login_old.status_code == 401

    # Verify: Login with NEW password should SUCCEED
    login_new = client.post("/api/userLogin", json={"username": username, "password": new_pass})
    assert login_new.status_code == 200

def test_change_password_wrong_old_password(client: TestClient):
    """Test failure when old password is incorrect"""
    username = "cp_wrong_old"
    create_test_user(client, username, "correct_password")

    payload = {
        "username": username,
        "old_password": "wrong_password",
        "new_password": "new_password"
    }
    response = client.post("/api/changePassword", json=payload)
    
    assert response.status_code == 401
    assert "Old password incorrect" in response.json()["detail"]

def test_change_password_user_not_found(client: TestClient):
    """Test changing password for non-existent user"""
    payload = {
        "username": "ghost_user",
        "old_password": "any",
        "new_password": "any"
    }
    response = client.post("/api/changePassword", json=payload)
    
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]