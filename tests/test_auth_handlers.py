import uuid
from datetime import datetime, timezone, timedelta
from xmlrpc.client import Fault

import pytest
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from mypy.typeops import false_only

from app.config import settings
from app.database.db import UserModel
from app.models import RefreshTokenInfo
from app.services.auth import (
    blacklisted_tokens,
    refresh_tokens,
    create_token_pair,
    create_jwt_token,
    generate_refresh_token,
    create_refresh_token,
)
from app.services.auth import (
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


def test_protected_route_without_token(client):
    """Test protected route without JWT token should fail."""
    response = client.get("/protected")
    assert response.status_code == 403  # HTTPBearer returns 403 when no credentials


def test_protected_route_with_valid_token(client, test_admin):
    """Test protected route with valid JWT token."""
    access_token = create_jwt_token(test_admin.uid)

    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "This is a protected route"
    assert response.json()["authenticated_user"] == str(test_admin.uid)


def test_protected_route_with_invalid_token(client):
    """Test protected route with invalid JWT token."""
    response = client.get(
        "/protected", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_login_with_valid_credentials(client, test_admin):
    """Test login endpoint with valid credentials returns both tokens."""
    response = client.post(
        "/login",
        json={"username": test_admin.username, "password": test_admin.username},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_admin.username
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
    refresh_tokens[expired_token] = RefreshTokenInfo(
        sub=uuid.uuid4(),
        exp=datetime.now(timezone.utc) - timedelta(hours=1),
        is_remember_me=False,
    )

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
    access_token = login_user["access_token"]

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
    access_token = login_user["access_token"]

    # Logout with both tokens
    response = client.post("/logout", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"

    # Verify both tokens were revoked
    assert access_token in blacklisted_tokens


def test_me_endpoint_with_valid_token(client, test_admin):
    """Test /me endpoint with valid JWT token."""
    access_token = create_jwt_token(test_admin.uid)
    response = client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "roles": test_admin.roles,
        "uid": str(test_admin.uid),
        "username": test_admin.username,
    }
    assert data == jsonable_encoder(UserModel.model_validate(test_admin.model_dump()))


def test_me_endpoint_without_token(client):
    """Test /me endpoint without JWT token should fail."""
    response = client.get("/me")
    assert response.status_code == 403


@pytest.mark.parametrize("rotation_enabled", [True, False])
def test_refresh_token_creates_valid_access_token(
    mocker, client, test_admin, rotation_enabled: bool
):
    """Test that refreshed access token can be used for protected routes."""
    # Get new access token using refresh token
    mocker.patch.object(settings, "ROTATE_REFRESH", rotation_enabled)
    refresh_token = create_refresh_token(test_admin.uid, True)
    response = client.post("/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()

    if rotation_enabled:
        assert refresh_token != response.json()["refresh_token"]
    else:
        assert refresh_token == response.json()["refresh_token"]


def test_expired_token_cleanup():
    """Test that expired tokens are cleaned up from blacklist."""

    # Add expired tokens
    expired_access_token = "expired_access_token"
    blacklisted_tokens[expired_access_token] = datetime.now(timezone.utc) - timedelta(
        hours=1
    )

    expired_refresh_token = "expired_refresh_token"
    refresh_tokens[expired_refresh_token] = RefreshTokenInfo(
        sub=uuid.uuid4(),
        exp=datetime.now(timezone.utc) - timedelta(hours=1),
        is_remember_me=False,
    )

    # Add valid tokens
    valid_access_token = "valid_access_token"
    blacklisted_tokens[valid_access_token] = datetime.now(timezone.utc) + timedelta(
        hours=1
    )

    valid_refresh_token = str(uuid.uuid4())
    refresh_tokens[valid_refresh_token] = RefreshTokenInfo(
        sub=valid_refresh_token,
        exp=datetime.now(timezone.utc) + timedelta(hours=1),
        is_remember_me=False,
    )

    # Run cleanup
    cleanup_expired_blacklisted_tokens()
    cleanup_expired_refresh_tokens()

    # Check that expired tokens were removed and valid tokens remain
    assert expired_access_token not in blacklisted_tokens
    assert valid_access_token in blacklisted_tokens
    assert expired_refresh_token not in refresh_tokens
    assert valid_refresh_token in refresh_tokens


def test_refresh_token_flow_integration(client, test_admin):
    """Test complete refresh token flow integration."""
    # 1. Login and get both tokens
    login_response = client.post(
        "/login", json={"username": test_admin.username, "password": "admin"}
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
        "/logout",
        headers=new_auth_headers,
    )
    assert logout_response.status_code == 200

    # 6. Verify tokens are revoked
    protected_response3 = client.get("/protected", headers=new_auth_headers)
    assert protected_response3.status_code == 401

    refresh_response2 = client.post("/refresh", json={"refresh_token": refresh_token})
    assert refresh_response2.status_code == 401
