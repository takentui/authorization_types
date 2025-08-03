from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Callable, Any, Awaitable, Coroutine

from app.config import settings
from app.db import UserFullModel, UserModel
from app.service import get_user

# Simple in-memory token blacklist store
# In production, use Redis or a database
blacklisted_tokens: Dict[str, datetime] = {}

# JWT Security
security = HTTPBearer()

# Global secret key to ensure consistency
_jwt_secret_key: Optional[str] = None


def create_jwt_token(user: UserFullModel, is_remember_me: bool) -> str:
    """Create a JWT token for the user."""
    if is_remember_me:
        expires_minutes = settings.JWT_EXPIRATION_REMEMBER_MINUTES
    else:
        expires_minutes = settings.JWT_EXPIRATION_DEFAULT_MINUTES

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    payload = {
        "sub": user.username,  # Subject (user identifier)
        "exp": int(expire.timestamp()),  # Expiration time as Unix timestamp
        "iat": int(
            datetime.now(timezone.utc).timestamp()
        ),  # Issued at as Unix timestamp
        "jti": secrets.token_urlsafe(16),  # JWT ID (unique identifier)
        "roles": user.roles,  # User roles
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def decode_jwt_token(token: str, algorithms: list[str] | None = None) -> Dict:
    """Decode and validate a JWT token."""
    try:
        # Check if token is blacklisted
        if token in blacklisted_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        if not algorithms:
            key = None
            options = {"verify_signature": False, "verify_exp": True}
        else:
            key = settings.JWT_SECRET_KEY
            options = {"verify_exp": True}

        # Decode the token
        payload = jwt.decode(token, key, algorithms=algorithms, options=options)
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserModel | None:
    """Extract and validate the current user from JWT token."""
    token = credentials.credentials
    payload = decode_jwt_token(token, ["HS256"])
    username = payload.get("sub")

    user = await get_user(username)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    return user


def get_user_by_role(roles: list[str] | str) -> Callable:
    async def wrapper(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> UserModel:
        user = await get_current_user(credentials)

        if isinstance(roles, str):
            access_roles = {
                roles,
            }
        else:
            access_roles = set(roles)

        if access_roles & set(user.roles):
            return user

        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You are not an admin!",
        )

    return wrapper


def get_current_user_unsign(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extract and validate the current user from JWT token."""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    username = payload.get("sub")

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    return username


def blacklist_token(token: str) -> None:
    """Add token to blacklist (for logout functionality)."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            blacklisted_tokens[token] = exp_datetime

            # Clean up expired blacklisted tokens
            cleanup_expired_blacklisted_tokens()
    except jwt.InvalidTokenError:
        # If token is invalid, no need to blacklist
        pass


def cleanup_expired_blacklisted_tokens() -> None:
    """Remove expired tokens from blacklist to prevent memory leaks."""
    current_time = datetime.now(timezone.utc)
    expired_tokens = [
        token
        for token, exp_time in blacklisted_tokens.items()
        if exp_time < current_time
    ]

    for token in expired_tokens:
        del blacklisted_tokens[token]


def create_jwt_token_unsigned(username: str) -> str:
    """Create an unsigned JWT token for the user."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": username,  # Subject (user identifier)
        "exp": int(expire.timestamp()),  # Expiration time as Unix timestamp
        "iat": int(
            datetime.now(timezone.utc).timestamp()
        ),  # Issued at as Unix timestamp
        "jti": secrets.token_urlsafe(16),  # JWT ID (unique identifier)
    }

    return jwt.encode(payload, None, algorithm="none")
