from datetime import datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette import status

from app.auth import get_user_by_role
from app.config import settings


@pytest.mark.asyncio
async def test_get_user_by_role(test_user):
    wrapper = get_user_by_role(test_user.roles)
    payload = {
        "sub": test_user.username,  # Subject (user identifier)
        "exp": int(
            (datetime.now() + timedelta(days=1)).timestamp()
        ),  # Expiration time as Unix timestamp
        "roles": test_user.roles,  # User roles
    }
    jwt_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    actual_user = await wrapper(
        HTTPAuthorizationCredentials(credentials=jwt_token, scheme="jwt")
    )

    assert test_user == actual_user


@pytest.mark.asyncio
async def test_get_user_by_role_error(test_user):
    wrapper = get_user_by_role("admin")
    payload = {
        "sub": test_user.username,  # Subject (user identifier)
        "exp": int(
            (datetime.now() + timedelta(days=1)).timestamp()
        ),  # Expiration time as Unix timestamp
        "roles": test_user.roles,  # User roles
    }
    jwt_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        await wrapper(HTTPAuthorizationCredentials(credentials=jwt_token, scheme="jwt"))

    assert exc.value.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
