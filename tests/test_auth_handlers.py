from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi import status
from fastapi.testclient import TestClient

from app.database import db
from app.main import app

BASE_URL = "http://localhost:8000"


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Welcome to the FastAPI Keycloak Auth Example"
    }


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_public_route(client):
    response = client.get("/public")
    assert response.status_code == status.HTTP_200_OK
    assert "public" in response.json()["message"]


def test_login_success(client, mock_keycloak_client):
    """Test successful login with Keycloak."""
    response = client.post(
        "/login", json={"username": "testuser", "password": "password"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "testuser"
    assert data["token_type"] == "bearer"
    assert data["message"] == "Login successful"


def test_login_invalid_credentials(client, mock_keycloak_client):
    """Test login with invalid credentials."""
    mock_keycloak_client.authenticate_user.side_effect = HTTPException(
        status_code=401, detail="Invalid username or password"
    )

    response = client.post(
        "/login", json={"username": "invalid", "password": "invalid"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid username or password" in response.json()["detail"]


def test_protected_route_without_token(client):
    """Test protected route without authentication token."""
    response = client.get("/protected")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_protected_route_with_valid_token(client, mock_keycloak_auth):
    """Test protected route with valid Keycloak token."""
    response = client.get(
        "/protected", headers={"Authorization": "Bearer mocked_access_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "protected" in data["message"]
    assert data["authenticated_user"] == "testuser"


def test_logout_and_blacklist(client, mock_keycloak_client):
    """Logout should blacklist token; further use of token must fail."""

    # 1. Logout using valid token
    response = client.post(
        "/logout", headers={"Authorization": "Bearer mocked_access_token"}
    )
    assert response.status_code == status.HTTP_200_OK

    # 2. Attempt to use same token again -> must be unauthorized due to blacklist
    response = client.get(
        "/protected", headers={"Authorization": "Bearer mocked_access_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_without_token(client):
    """Test logout without authentication token."""
    response = client.post("/logout")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_info_success(client, mock_keycloak_auth):
    """Test getting user info with valid token."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "keycloak_id": "test-user-id",
        "roles": ["user"],
        "created_at": "2023-01-01T00:00:00",
    }
    db.set("users", "testuser", user_data)

    response = client.get(
        "/me", headers={"Authorization": "Bearer mocked_access_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert "user_data" in data
    assert "message" in data


def test_get_user_info_user_not_found(client, mock_keycloak_auth):
    """Test getting user info when user not in database."""
    response = client.get(
        "/me", headers={"Authorization": "Bearer mocked_access_token"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]


def test_get_user_info_without_token(client):
    """Test getting user info without authentication token."""
    response = client.get("/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_keycloak_service_error(client, mock_keycloak_client):
    """Test handling of Keycloak service errors."""
    mock_keycloak_client.authenticate_user.side_effect = Exception(
        "Service unavailable"
    )

    response = client.post(
        "/login", json={"username": "testuser", "password": "password"}
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Authentication service error" in response.json()["detail"]
