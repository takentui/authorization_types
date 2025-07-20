import pytest
import base64
from fastapi import status, Cookie
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from passlib.handlers.sha2_crypt import sha256_crypt

from app.config import settings
from app.db import USERS
from app.main import app
from app.auth import active_sessions, get_random_session_token
from app.models import ActiveSessionModel, UserModel, LoginRequest

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "password"


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to the FastAPI Session Auth Example"}


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_public_route(client):
    """Test public route that doesn't require authentication."""
    response = client.get("/public")
    assert response.status_code == 200
    assert response.json()["message"] == "This is a public route"


def test_protected_route_without_cookie(client):
    """Test protected route without cookie should fail."""
    response = client.get("/protected")
    assert response.status_code == 401


def test_protected_route_with_valid_cookie(client, session_token):
    """Test protected route with valid cookie."""
    response = client.get("/protected", cookies={"session_token": session_token})
    assert response.status_code == 200
    assert response.json()["message"] == "This is a protected route"
    assert response.json()["authenticated_user"] == USERS[0].username


def test_protected_route_with_invalid_cookie(client):
    """Test protected route with invalid cookie."""
    response = client.get("/protected", cookies={"session_token": "invalid_token"})
    assert response.status_code == 401


def test_login_with_valid_credentials(client):
    """Test login endpoint with valid credentials."""
    username = "test_user"
    USERS[0] = UserModel(username=username, password=sha256_crypt.hash("1"))
    response = client.post("/login", json={"username": username, "password": "1"})
    assert response.status_code == 200
    assert response.json()["username"] == username
    assert "session_token" in response.cookies

    # Verify session was created
    session_token = response.cookies["session_token"]
    assert session_token in active_sessions
    assert active_sessions[session_token].user_id == 0

    del USERS[0]


def test_login_with_invalid_credentials(client):
    """Test login endpoint with invalid credentials."""
    response = client.post(
        "/login", json={"username": "wrong", "password": "credentials"}
    )
    assert response.status_code == 401


def test_logout_without_cookie(client):
    """Test logout endpoint without cookie should fail."""
    response = client.post("/logout")
    assert response.status_code == 401


def test_logout_with_valid_cookie(client):
    """Test logout endpoint with valid cookie."""
    token = get_random_session_token()
    active_sessions[token] = ActiveSessionModel(
        user_id=0,
        expired=0,
        remember_me=False,
    )
    # Logout with the cookie
    response = client.post("/logout", cookies={"session_token": token})
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"

    # Verify session was removed
    assert token not in active_sessions

    # Verify cookie was cleared
    assert not response.cookies


@pytest.mark.parametrize(
    "malformed_header",
    [
        {"Authorization": "Basic invalid-base64"},
        {"Authorization": "NotBasic valid-base64"},
        {"Authorization": "Bearer token"},
    ],
)
def test_protected_endpoint_malformed_auth(client, malformed_header):
    response = client.get("/protected", headers=malformed_header)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_handler(client):
    login = LoginRequest(
        username="test_user",
        password="1",
    )

    len_users = len(USERS)

    response = client.post("/registration", json=jsonable_encoder(login))
    assert response.status_code == 200
    assert len_users < len(USERS)
    assert USERS[len(USERS)].username == login.username
    assert sha256_crypt.verify(login.password, USERS[len(USERS)].password)


def test_register_bad_request(client, session_token):
    login = LoginRequest(
        username="test",
        password="1",
    )

    response = client.post("/registration", json=jsonable_encoder(login))
    assert response.status_code == 400
