import datetime
import logging

from fastapi import HTTPException, status, Cookie, Response
import secrets
import string
from typing import Optional, Dict, cast

from passlib.handlers.sha2_crypt import sha256_crypt

from app.config import settings
from app.db import USERS, get_user_id
from app.models import LoginRequest, UserModel, ActiveSessionModel
from app.utils import get_ttl


logger = logging.getLogger("root")

# Simple in-memory session store
# In production, use Redis or a database
active_sessions: Dict[str, ActiveSessionModel] = {}


def get_random_session_token(length: int = 32) -> str:
    """Generate a random session token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def validate_credentials(username: str, password: str) -> bool:
    for user in USERS.values():
        if user.username == username:
            return sha256_crypt.verify(password, user.password)
    return False


def create_session(login_request: LoginRequest, response: Response) -> str:
    """Create a new session for the user and set the session cookie."""
    ttl = get_ttl(login_request.remember_me)

    session_token = get_random_session_token()
    active_sessions[session_token] = ActiveSessionModel(
        user_id=cast(int, get_user_id(login_request.username)),
        expired=int(datetime.datetime.now().timestamp() + ttl),
        remember_me=login_request.remember_me,
    )

    set_cookie(response, session_token, ttl)

    return session_token


def set_cookie(response: Response, session_token: str, ttl: int) -> None:
    # Set the session cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=settings.COOKIE_HTTPONLY,  # Prevent JavaScript access
        max_age=ttl,  # 30 minutes
        # secure=settings.COOKIE_SECURE,  # Uncomment in production (HTTPS only)
        samesite=settings.COOKIE_SAMESITE,  # Prevent CSRF
        domain=settings.COOKIE_DOMAIN,
    )


def get_current_user_from_cookie(
    response: Response, session_token: Optional[str] = Cookie(None)
) -> int:
    """Validate the session token from cookie."""
    if session_token is None or session_token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session or session expired",
        )

    session = active_sessions[session_token]
    if session.expired <= datetime.datetime.now().timestamp() + 5 * 60:
        ttl = get_ttl(session.remember_me)
        session.expired = int(datetime.datetime.now().timestamp() + ttl)
        logger.info(
            "Update session expiration %s, new expired %s",
            session_token,
            session.expired,
        )
        set_cookie(response, session_token, ttl)

    return session.user_id


def end_session(session_token: str, response: Response) -> None:
    """End a user session and clear the cookie."""
    if session_token in active_sessions:
        del active_sessions[session_token]

    response.delete_cookie(key="session_token")


def create_user(username: str, password: str) -> UserModel:
    if not get_user_id(username) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user credentials",
        )

    user = UserModel(username=username, password=sha256_crypt.hash(password))
    USERS[len(USERS) + 1] = user
    return user
