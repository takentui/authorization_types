import logging
import secrets

from fastapi import HTTPException
from passlib.handlers.sha2_crypt import sha256_crypt
from pydantic import UUID4
from starlette import status

from app.database.db import DB_USERS, UserFullModel, UserModel
from app.models import RegistrationRequest
from app.services.helpers import generate_user_uid


def _get_user_by_username(username: str) -> UserFullModel | None:
    for user in DB_USERS.values():
        if user.username == username:
            return user
    return None


def validate_credentials(username: str, password: str) -> UUID4 | None:
    user = _get_user_by_username(username)
    if user and sha256_crypt.verify(password, user.password_hash):
        return user.uid

    return None


def get_user(user_uid: UUID4) -> UserModel:
    if str(user_uid) not in DB_USERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not exists"
        )
    return UserModel.model_validate(DB_USERS[str(user_uid)])


def create_user(payload: RegistrationRequest) -> UUID4:
    if _get_user_by_username(payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    uid = generate_user_uid()
    DB_USERS[str(uid)] = UserFullModel(
        uid=uid,
        username=payload.username,
        roles=payload.roles,
        password_hash=sha256_crypt.hash(payload.password),
    )
    logging.info("User created %s", uid)
    return uid
