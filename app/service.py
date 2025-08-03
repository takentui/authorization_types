from fastapi import HTTPException
from passlib.handlers.sha2_crypt import sha256_crypt
from starlette import status

from app.db import UserFullModel, users, UserModel
from app.models import RegisterRequest


async def get_user(username: str) -> UserModel | None:
    for user in users.values():
        if user.username == username:
            return user
    return None


async def register_user(register_request: RegisterRequest) -> UserFullModel:
    # Validate credentials
    user = await get_user(register_request.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    new_user = UserFullModel(
        username=register_request.username,
        password_hash=sha256_crypt.hash(register_request.password),
        roles=register_request.roles,
    )
    users[len(users.keys())] = new_user
    return new_user


def get_user_by_credentials(username: str, password: str) -> UserFullModel | None:
    for user in users.values():
        if user.username == username and sha256_crypt.verify(
            password, user.password_hash
        ):
            return user
    return None
