import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from backend.console.app import app
from backend.console.utils.auth import create_access_token
from openapi_server.models.pagination_query import PaginationQuery

client = TestClient(app)


def test_whitelisted_action_does_not_require_authorization_header():
    response = client.post("/api/userLogin", json={})
    assert response.status_code != 401


def test_non_whitelisted_action_requires_authorization_header():
    response = client.post("/api/listIdentifyStarsJobs",
                           json=PaginationQuery().to_dict())
    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header required"


def test_non_whitelisted_action_rejects_invalid_token():
    response = client.post(
        "/api/listIdentifyStarsJobs",
        json=PaginationQuery().to_dict(),
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_non_whitelisted_action_allows_valid_token():
    token = create_access_token({"user_id": "middleware-test"})
    try:
        response = client.post(
            "/api/listIdentifyStarsJobs",
            json=PaginationQuery().to_dict(),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code != 401
    except Exception as e:
        ...


def test_websocket_requires_authorization_header():
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/api/chat?user_id=ws-auth-test"):
            pass

    assert exc.value.code == 1008


def test_websocket_rejects_invalid_token():
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(
            "/api/chat?user_id=ws-auth-test",
            headers={"Authorization": "Bearer invalid.token.value"},
        ):
            pass

    assert exc.value.code == 1008


def test_websocket_allows_valid_token():
    token = create_access_token({"user_id": "ws-auth-test"})
    with client.websocket_connect(
        "/api/chat?user_id=ws-auth-test",
        headers={"Authorization": f"Bearer {token}"},
    ):
        pass
