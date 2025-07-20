import pytest
from fastapi.testclient import TestClient

from app.db import USERS
from app.main import app
from app.auth import active_sessions, get_random_session_token
from app.models import UserModel, ActiveSessionModel


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
    response = client.post("/login", json={"username": "admin", "password": "password"})
    return response


@pytest.fixture
def session_token():
    USERS[0] = UserModel(username="test", password="")
    token = get_random_session_token()
    active_sessions[token] = ActiveSessionModel(
        user_id=0,
        expired=0,
        remember_me=False,
    )
    yield token

    del active_sessions[token]
    del USERS[0]
