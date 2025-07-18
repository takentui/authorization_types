from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

from passlib.handlers.sha2_crypt import sha256_crypt

from app.config import settings
from app.db import USERS

# Initialize HTTP Basic security
security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Dependency to validate basic auth credentials.

    Returns username on success, raises 401 exception on failure.
    """
    if not credentials.username in USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown username",
            headers={"WWW-Authenticate": "Basic"},
        )

    is_correct_password = sha256_crypt.verify(
        credentials.password, USERS.get(credentials.username)
    )

    if not is_correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
