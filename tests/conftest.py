import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth import blacklisted_tokens, refresh_tokens
from app.database.users import clear_oauth_users


@pytest.fixture(autouse=True)
def clear_token_stores():
    """Clear all token stores and OAuth users before each test."""
    blacklisted_tokens.clear()
    refresh_tokens.clear()
    clear_oauth_users()
    yield


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def login_user(client):
    """Login a user and return both access and refresh tokens."""
    response = client.post("/login", json={"username": "admin", "password": "password"})
    return response


@pytest.fixture
def auth_headers(login_user):
    """Create authorization headers with JWT token."""
    token = login_user.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def refresh_token(login_user):
    """Get refresh token from login response."""
    return login_user.json()["refresh_token"]
