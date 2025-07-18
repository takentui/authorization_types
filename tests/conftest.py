import base64

import pytest
from fastapi.testclient import TestClient
from passlib.handlers.sha2_crypt import sha256_crypt

from app.db import USERS
from app.main import app

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "password"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    test = "test_user"
    USERS[test] = sha256_crypt.hash(test)
    credentials = f"{test}:{test}"
    encoded = base64.b64encode(credentials.encode()).decode()
    yield {"Authorization": f"Basic {encoded}"}
    del USERS[test]


@pytest.fixture
def invalid_auth_headers():
    credentials = "wronguser:wrongpass"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}
