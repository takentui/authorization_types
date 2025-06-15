import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from fastapi import HTTPException


@pytest.fixture
def client():
    """Test client."""
    return TestClient(app)


@pytest.fixture
def mock_keycloak_oauth_user():
    """Mock Keycloak OAuth user data."""
    return {
        "sub": "keycloak-user-123",
        "preferred_username": "oauth_testuser",
        "email": "oauth_test@example.com",
        "given_name": "OAuth",
        "family_name": "Test",
        "realm_access": {"roles": ["user", "oauth_user"]},
    }


def test_oauth_integration_with_keycloak(
    client, mock_keycloak_client, mock_keycloak_oauth_user
):
    """Test OAuth integration through Keycloak."""
    mock_keycloak_client.authenticate_user.return_value = {
        "access_token": "oauth_access_token",
        "token_type": "bearer",
        "expires_in": 3600,
    }

    mock_keycloak_client.validate_token.return_value = mock_keycloak_oauth_user

    response = client.post(
        "/login", json={"username": "oauth_testuser", "password": "oauth_password"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "oauth_testuser"


def test_oauth_user_protected_access(client, mock_keycloak_auth):
    """Test OAuth user accessing protected routes."""
    response = client.get(
        "/protected", headers={"Authorization": "Bearer oauth_access_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["authenticated_user"] == "testuser"


def test_oauth_logout(client, mock_keycloak_auth):
    """Test OAuth user logout."""
    response = client.post(
        "/logout", headers={"Authorization": "Bearer oauth_access_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Logout successful"


def test_keycloak_oauth_error_handling(client, mock_keycloak_client):
    """Test error handling for OAuth through Keycloak."""
    mock_keycloak_client.authenticate_user.side_effect = HTTPException(
        status_code=401, detail="OAuth authentication failed"
    )

    response = client.post(
        "/login", json={"username": "oauth_user", "password": "invalid"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "OAuth authentication failed" in response.json()["detail"]
