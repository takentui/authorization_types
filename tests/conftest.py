import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth import blacklisted_tokens


@pytest.fixture(autouse=True)
def clear_blacklisted_tokens():
    """Clear all blacklisted tokens before each test."""
    blacklisted_tokens.clear()
    yield


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def login_user(client):
    """Login a user and return the JWT token."""
    response = client.post(
        "/login",
        json={"username": "admin", "password": "password"}
    )
    return response


@pytest.fixture
def auth_headers(login_user):
    """Create authorization headers with JWT token."""
    token = login_user.json()["access_token"]
    return {"Authorization": f"Bearer {token}"} 