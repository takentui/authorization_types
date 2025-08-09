import uuid

import pytest
from fastapi.testclient import TestClient
from passlib.handlers.sha2_crypt import sha256_crypt

from app.database.db import DB_USERS, UserFullModel
from app.main import app
from app.services.auth import blacklisted_tokens, refresh_tokens, create_token_pair


@pytest.fixture(autouse=True)
def clear_token_stores():
    """Clear all token stores before each test."""
    blacklisted_tokens.clear()
    refresh_tokens.clear()
    yield


@pytest.fixture
def clear_db():
    DB_USERS.clear()
    yield
    DB_USERS.clear()


@pytest.mark.usefixtures("clear_db")
@pytest.fixture
def test_admin():
    uid = uuid.uuid4()
    DB_USERS[str(uid)] = UserFullModel(
        uid=uid,
        username="admin",
        password_hash=sha256_crypt.hash("admin"),
        roles=["admin"],
    )
    return DB_USERS[str(uid)]


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def login_user(test_admin):
    """Login a user and return both access and refresh tokens."""
    access_token, refresh_token = create_token_pair(test_admin.uid, False)
    return {"access_token": access_token, "refresh_token": refresh_token}


@pytest.fixture
def auth_headers(login_user):
    """Create authorization headers with JWT token."""
    token = login_user["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def refresh_token(login_user):
    """Get refresh token from login response."""
    return login_user["refresh_token"]
