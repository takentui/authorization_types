import functools
from typing import Callable

from fastapi import HTTPException, Depends
from pydantic.v1 import UUID4
from starlette import status

from app.services.auth import (
    create_refresh_token,
    create_jwt_token,
    create_token_pair,
    get_current_user,
)
from app.models import (
    RegistrationRequest,
    RefreshTokenResponse,
    LoginRequest,
    LoginResponse,
)
from app.services.users import create_user, validate_credentials, get_user


def register_new_user(payload: RegistrationRequest) -> RefreshTokenResponse:
    uid = create_user(payload)
    # Create new token pair
    new_refresh_token = create_refresh_token(uid, is_remember_me=payload.is_remember_me)
    new_access_token = create_jwt_token(uid)

    return RefreshTokenResponse(
        access_token=new_access_token, refresh_token=new_refresh_token
    )


def authorize(login_request: LoginRequest) -> LoginResponse:
    """Login endpoint that returns both access and refresh tokens."""
    # Validate credentials
    user_uid = validate_credentials(login_request.username, login_request.password)

    if not user_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create both access and refresh tokens
    access_token, refresh_token = create_token_pair(
        user_uid, login_request.is_remember_me
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        username=login_request.username,
    )


def roles(access_roles: set[str]) -> Callable:
    def decorator(handler):
        @functools.wraps(handler)
        async def wrapper(*args, user_uid: UUID4 = Depends(get_current_user), **kwargs):
            user = get_user(user_uid)

            if set(user.roles) & access_roles:
                return await handler(*args, user_uid=user_uid, **kwargs)

            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Method is not allowed",
            )

        return wrapper

    return decorator
