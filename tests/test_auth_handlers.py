import datetime

import jwt
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from passlib.handlers.sha2_crypt import sha256_crypt

from app.config import settings
from app.db import users, UserFullModel
from app.main import app
from app.auth import blacklisted_tokens


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to the FastAPI JWT Auth Example"}


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
    assert response.json()["authenticated_user"] == "test"


def test_protected_route_with_invalid_token(client):
    """Test protected route with invalid JWT token."""
    response = client.get(
        "/protected", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_login_with_valid_credentials(client, test_user):
    """Test login endpoint with valid credentials."""
    response = client.post("/login", json={"username": "test", "password": "test"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test"
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert len(data["access_token"]) > 0


def test_login_with_invalid_credentials(client):
    """Test login endpoint with invalid credentials."""
    response = client.post(
        "/login", json={"username": "wrong", "password": "credentials"}
    )
    assert response.status_code == 401


def test_logout_without_token(client):
    """Test logout endpoint without JWT token should fail."""
    response = client.post("/logout")
    assert response.status_code == 403  # HTTPBearer returns 403 when no credentials


def test_logout_with_valid_token(client, auth_headers):
    """Test logout endpoint with valid JWT token."""
    token = auth_headers.get("Authorization").split("Bearer ")[1]

    # Logout with the token
    response = client.post("/logout", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"

    # Verify token was blacklisted
    assert token in blacklisted_tokens


def test_api_with_blacklisted_token(client, auth_headers):
    """Test logout endpoint with valid JWT token."""
    token = auth_headers.get("Authorization").split("Bearer ")[1]

    blacklisted_tokens[token] = datetime.datetime.now()
    # Try to use the token again - should fail
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 401


def test_me_endpoint_with_valid_token(client, auth_headers):
    """Test /me endpoint with valid JWT token."""
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == users[0].username


def test_me_endpoint_without_token(client):
    """Test /me endpoint without JWT token should fail."""
    response = client.get("/me")
    assert response.status_code == 403


def test_expired_token_cleanup():
    """Test that expired tokens are cleaned up from blacklist."""
    from app.auth import cleanup_expired_blacklisted_tokens
    from datetime import datetime, timezone, timedelta

    # Add an expired token
    expired_token = "expired_token"
    blacklisted_tokens[expired_token] = datetime.now(timezone.utc) - timedelta(hours=1)

    # Add a valid token
    valid_token = "valid_token"
    blacklisted_tokens[valid_token] = datetime.now(timezone.utc) + timedelta(hours=1)

    # Run cleanup
    cleanup_expired_blacklisted_tokens()

    # Check that expired token was removed and valid token remains
    assert expired_token not in blacklisted_tokens
    assert valid_token in blacklisted_tokens


@pytest.mark.usefixture("clear_db")
def test_register_user(client):
    response = client.post(
        "/users", json={"username": "test", "password": "test", "roles": ["test"]}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "test"
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert len(data["access_token"]) > 0
    assert len(users) > 0


def test_register_user_already_exists(client, test_user):
    response = client.post(
        "/users", json={"username": "test", "password": "test", "roles": ["test"]}
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert data.get("detail") == "User already exists"


def test_admin_handler(client, clear_db):
    users[0] = UserFullModel(
        username="test", password_hash=sha256_crypt.hash("test"), roles=["admin"]
    )

    payload = {
        "sub": users[0].username,  # Subject (user identifier)
        "exp": int(
            (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()
        ),  # Expiration time as Unix timestamp
        "roles": users[0].roles,  # User roles
    }

    response = client.get(
        "/admin",
        headers={
            "Authorization": f"Bearer {jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')}"
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "It's for admin only!"}


def test_admin_handler_not_allowed(client, auth_headers):
    response = client.get(
        "/admin",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
