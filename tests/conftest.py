import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth import active_sessions


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear all sessions before each test."""
    active_sessions.clear()
    yield


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def login_user(client):
    """Login a user and return the response with session cookie."""
    response = client.post(
        "/login",
        json={"username": "admin", "password": "password"}
    )
    return response 