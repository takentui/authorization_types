import pytest
from fastapi.encoders import jsonable_encoder
from starlette import status

from app.db import OBJECTS, DBObjectModel, ObjectModel


def test_get_objects_endpoint_invalid_auth(client, invalid_auth_headers):
    response = client.get("/api/objects/1", headers=invalid_auth_headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_objects_endpoint_valid_auth(client, auth_headers):
    OBJECTS[1] = DBObjectModel(
        field1="test",
        field2=1,
        username="test_user",
    )
    response = client.get("/api/objects/1", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == jsonable_encoder(
        ObjectModel(field1=OBJECTS[1].field1, field2=OBJECTS[1].field2)
    )
    del OBJECTS[1]


def test_get_objects_endpoint_not_found(client, auth_headers):
    response = client.get("/api/objects/0", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_objects_endpoint_invalid_auth(client, invalid_auth_headers):
    response = client.post("/api/objects", headers=invalid_auth_headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_objects_endpoint_happy_path(client, auth_headers):
    previous_count = len(OBJECTS)
    response = client.post(
        "/api/objects",
        json=jsonable_encoder(ObjectModel(field1="test", field2=1)),
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(OBJECTS) == previous_count + 1
    assert jsonable_encoder(OBJECTS[len(OBJECTS)]) == jsonable_encoder(
        DBObjectModel(field1="test", field2=1, username="test_user")
    )
