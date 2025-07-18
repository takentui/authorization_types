import pytest
from fastapi import status

USERNAME = "test_user"


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to the FastAPI Basic Auth Example"}


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


def test_public_endpoint(client):
    response = client.get("/public")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert data["message"] == "This is a public route"
    assert "data" in data
    assert data["data"] == "public information"


def test_protected_endpoint_no_auth(client):
    response = client.get("/protected")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_protected_endpoint_invalid_auth(client, invalid_auth_headers):
    response = client.get("/protected", headers=invalid_auth_headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Basic"


def test_protected_endpoint_valid_auth(client, auth_headers):
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert data["message"] == "This is a protected route"
    assert "data" in data
    assert data["data"] == "secret information"
    assert "authenticated_user" in data
    assert data["authenticated_user"] == USERNAME


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
