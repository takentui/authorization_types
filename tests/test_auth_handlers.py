from datetime import datetime, timezone, timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.auth import blacklisted_tokens, refresh_tokens
from app.auth import (
    cleanup_expired_blacklisted_tokens,
    cleanup_expired_refresh_tokens,
)
from app.main import app

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "password"


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Welcome to the FastAPI JWT Auth Example with OAuth"
    }


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_public_route(client):
    """Test public route that doesn't require authentication."""
    response = client.get("/public")
    assert response.status_code == 200
    assert response.json()["message"] == "This is a public route"


def test_protected_route_without_token(client):
    """Test protected route without JWT token should fail."""
    response = client.get("/protected")
    assert response.status_code == 403  # HTTPBearer returns 403 when no credentials


def test_protected_route_with_valid_token(client, auth_headers):
    """Test protected route with valid JWT token."""
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "This is a protected route"
    assert response.json()["authenticated_user"] == "admin"


def test_protected_route_with_invalid_token(client):
    """Test protected route with invalid JWT token."""
    response = client.get(
        "/protected", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_login_with_valid_credentials(client):
    """Test login endpoint with valid credentials returns both tokens."""
    response = client.post("/login", json={"username": "admin", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert "refresh_token" in data
    assert len(data["access_token"]) > 0
    assert len(data["refresh_token"]) > 0


def test_login_with_invalid_credentials(client):
    """Test login endpoint with invalid credentials."""
    response = client.post(
        "/login", json={"username": "wrong", "password": "credentials"}
    )
    assert response.status_code == 401


def test_refresh_token_endpoint_with_valid_token(client, refresh_token):
    """Test refresh token endpoint with valid refresh token."""
    response = client.post("/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["message"] == "Token refreshed successfully"
    assert len(data["access_token"]) > 0


def test_refresh_token_endpoint_with_invalid_token(client):
    """Test refresh token endpoint with invalid refresh token."""
    response = client.post("/refresh", json={"refresh_token": "invalid_refresh_token"})
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]


def test_refresh_token_endpoint_with_expired_token(client):
    """Test refresh token endpoint with expired refresh token."""
    # Create an expired refresh token manually
    expired_token = "expired_refresh_token"
    refresh_tokens[expired_token] = {
        "username": "admin",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }

    response = client.post("/refresh", json={"refresh_token": expired_token})
    assert response.status_code == 401
    assert "Refresh token has expired" in response.json()["detail"]

    # Verify expired token was removed
    assert expired_token not in refresh_tokens


def test_logout_without_token(client):
    """Test logout endpoint without JWT token should fail."""
    response = client.post("/logout")
    assert response.status_code == 403  # HTTPBearer returns 403 when no credentials


def test_logout_with_valid_token_only(client, auth_headers, login_user):
    """Test logout endpoint with only access token."""
    access_token = login_user.json()["access_token"]

    # Logout with only access token
    response = client.post("/logout", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"

    # Verify access token was blacklisted
    assert access_token in blacklisted_tokens

    # Try to use the access token again - should fail
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 401


def test_logout_with_both_tokens(client, auth_headers, login_user, refresh_token):
    """Test logout endpoint with both access and refresh tokens."""
    access_token = login_user.json()["access_token"]

    # Logout with both tokens
    response = client.post(
        "/logout", headers=auth_headers, json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"

    # Verify both tokens were revoked
    assert access_token in blacklisted_tokens
    assert refresh_token not in refresh_tokens

    # Try to use refresh token - should fail
    response = client.post("/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401


def test_me_endpoint_with_valid_token(client, auth_headers):
    """Test /me endpoint with valid JWT token."""
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert "message" in data


def test_me_endpoint_without_token(client):
    """Test /me endpoint without JWT token should fail."""
    response = client.get("/me")
    assert response.status_code == 403


def test_refresh_token_creates_valid_access_token(client, refresh_token):
    """Test that refreshed access token can be used for protected routes."""
    # Get new access token using refresh token
    response = client.post("/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    new_access_token = response.json()["access_token"]

    # Use new access token for protected route
    new_auth_headers = {"Authorization": f"Bearer {new_access_token}"}
    response = client.get("/protected", headers=new_auth_headers)
    assert response.status_code == 200
    assert response.json()["authenticated_user"] == "admin"


def test_expired_token_cleanup():
    """Test that expired tokens are cleaned up from blacklist."""

    # Add expired tokens
    expired_access_token = "expired_access_token"
    blacklisted_tokens[expired_access_token] = datetime.now(timezone.utc) - timedelta(
        hours=1
    )

    expired_refresh_token = "expired_refresh_token"
    refresh_tokens[expired_refresh_token] = {
        "username": "admin",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }

    # Add valid tokens
    valid_access_token = "valid_access_token"
    blacklisted_tokens[valid_access_token] = datetime.now(timezone.utc) + timedelta(
        hours=1
    )

    valid_refresh_token = "valid_refresh_token"
    refresh_tokens[valid_refresh_token] = {
        "username": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }

    # Run cleanup
    cleanup_expired_blacklisted_tokens()
    cleanup_expired_refresh_tokens()

    # Check that expired tokens were removed and valid tokens remain
    assert expired_access_token not in blacklisted_tokens
    assert valid_access_token in blacklisted_tokens
    assert expired_refresh_token not in refresh_tokens
    assert valid_refresh_token in refresh_tokens


def test_refresh_token_flow_integration(client):
    """Test complete refresh token flow integration."""
    # 1. Login and get both tokens
    login_response = client.post(
        "/login", json={"username": "admin", "password": "password"}
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]

    # 2. Use access token for protected route
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    protected_response = client.get("/protected", headers=auth_headers)
    assert protected_response.status_code == 200

    # 3. Refresh the access token
    refresh_response = client.post("/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    new_access_token = refresh_response.json()["access_token"]
    assert new_access_token != access_token  # Should be different

    # 4. Use new access token
    new_auth_headers = {"Authorization": f"Bearer {new_access_token}"}
    protected_response2 = client.get("/protected", headers=new_auth_headers)
    assert protected_response2.status_code == 200

    # 5. Logout with both tokens
    logout_response = client.post(
        "/logout", headers=new_auth_headers, json={"refresh_token": refresh_token}
    )
    assert logout_response.status_code == 200

    # 6. Verify tokens are revoked
    protected_response3 = client.get("/protected", headers=new_auth_headers)
    assert protected_response3.status_code == 401

    refresh_response2 = client.post("/refresh", json={"refresh_token": refresh_token})
    assert refresh_response2.status_code == 401
