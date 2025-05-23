import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from app.auth import blacklisted_tokens

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "password"


@pytest.fixture
def client():
    return TestClient(app)


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
    assert response.json()["authenticated_user"] == "admin"


def test_protected_route_with_invalid_token(client):
    """Test protected route with invalid JWT token."""
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_login_with_valid_credentials(client):
    """Test login endpoint with valid credentials."""
    response = client.post(
        "/login",
        json={"username": "admin", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert len(data["access_token"]) > 0


def test_login_with_invalid_credentials(client):
    """Test login endpoint with invalid credentials."""
    response = client.post(
        "/login",
        json={"username": "wrong", "password": "credentials"}
    )
    assert response.status_code == 401


def test_logout_without_token(client):
    """Test logout endpoint without JWT token should fail."""
    response = client.post("/logout")
    assert response.status_code == 403  # HTTPBearer returns 403 when no credentials


def test_logout_with_valid_token(client, auth_headers, login_user):
    """Test logout endpoint with valid JWT token."""
    token = login_user.json()["access_token"]
    
    # Logout with the token
    response = client.post("/logout", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"
    
    # Verify token was blacklisted
    assert token in blacklisted_tokens
    
    # Try to use the token again - should fail
    response = client.get("/protected", headers=auth_headers)
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