from datetime import datetime, timedelta
from typing import Generator

import jwt
import pytest
from fastapi.testclient import TestClient
from passlib.handlers.sha2_crypt import sha256_crypt

from app.config import settings
from app.db import UserFullModel, users
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
def clear_db() -> Generator[None, None, None]:
    users.clear()
    yield
    users.clear()


@pytest.fixture
def test_user(clear_db) -> Generator[UserFullModel, None, None]:
    users[0] = UserFullModel(
        username="test", password_hash=sha256_crypt.hash("test"), roles=["test"]
    )
    yield users[0]


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers with JWT token."""

    payload = {
        "sub": test_user.username,  # Subject (user identifier)
        "exp": int(
            (datetime.now() + timedelta(days=1)).timestamp()
        ),  # Expiration time as Unix timestamp
        "roles": test_user.roles,  # User roles
    }

    return {
        "Authorization": f"Bearer {jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')}"
    }
