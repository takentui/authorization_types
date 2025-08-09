import logging
import uuid

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple

from pydantic import UUID4

from app.config import settings
from app.models import RefreshTokenResponse, RefreshTokenInfo

# Simple in-memory token blacklist store
# In production, use Redis or a database
blacklisted_tokens: Dict[str, datetime] = {}

# Refresh token store (in production, use database)
refresh_tokens: Dict[
    str, RefreshTokenInfo
] = {}  # token -> {"username": str, "exp": datetime}

# JWT Security
security = HTTPBearer()


def create_jwt_token(
    uid: UUID4,
) -> str:
    """Create a JWT access token for the user."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(uid),  # Subject (user identifier)
        "exp": int(expire.timestamp()),  # Expiration time as Unix timestamp
        "iat": int(
            datetime.now(timezone.utc).timestamp()
        ),  # Issued at as Unix timestamp
        "jti": secrets.token_urlsafe(16),  # JWT ID (unique identifier)
        "type": "access",  # Token type
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def create_refresh_token(uid: UUID4, is_remember_me: bool) -> str:
    """Create a refresh token for the user."""
    if is_remember_me:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_EXPIRE_REMEMBER_DAYS
        )
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_EXPIRE_DEFAULT_DAYS
        )

    refresh_token = str(uuid.uuid4())

    # Store refresh token info
    refresh_tokens[refresh_token] = RefreshTokenInfo(
        sub=uid,
        exp=expire,
        is_remember_me=is_remember_me,
    )

    logging.info("Generated token: %s , exp: %s", refresh_token, expire)
    # Clean up expired refresh tokens
    cleanup_expired_refresh_tokens()

    return refresh_token


def create_token_pair(user_uid: UUID4, is_remember_me: bool) -> Tuple[str, str]:
    """Create both access and refresh tokens for the user."""
    access_token = create_jwt_token(user_uid)
    refresh_token = create_refresh_token(user_uid, is_remember_me)
    return access_token, refresh_token


def validate_refresh_token(refresh_token: str) -> RefreshTokenInfo:
    """Validate refresh token and return username."""
    if refresh_token not in refresh_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    token_info = refresh_tokens[refresh_token]

    # Check if token is expired
    if token_info.exp < datetime.now(timezone.utc):
        del refresh_tokens[refresh_token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired"
        )

    return token_info


def generate_refresh_token(refresh_token: str) -> RefreshTokenResponse:
    token_info = validate_refresh_token(refresh_token)

    # Create new token pair
    new_access_token = create_jwt_token(token_info.sub)
    if settings.ROTATE_REFRESH:
        new_refresh_token = create_refresh_token(
            token_info.sub, token_info.is_remember_me
        )
        # Remove expired token
        del refresh_tokens[refresh_token]
    else:
        new_refresh_token = refresh_token

    return RefreshTokenResponse(
        access_token=new_access_token, refresh_token=new_refresh_token
    )


def revoke_refresh_token(refresh_token: str) -> None:
    """Revoke a refresh token (for logout)."""
    if refresh_token in refresh_tokens:
        del refresh_tokens[refresh_token]


def decode_jwt_token(token: str) -> Dict:
    """Decode and validate a JWT token."""
    try:
        # Check if token is blacklisted
        if token in blacklisted_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        # Decode the token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID4:
    """Extract and validate the current user from JWT token."""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    user_uid = payload.get("sub")

    if user_uid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    return UUID4(user_uid)


def blacklist_token(token: str) -> None:
    """Add token to blacklist (for logout functionality)."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        exp_timestamp = payload.get("exp")
        sub = payload.get("sub")
        cleanup_expired_refresh_tokens(sub)
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


def cleanup_expired_refresh_tokens(sub: str | None = None) -> None:
    """Remove expired refresh tokens to prevent memory leaks."""
    current_time = datetime.now(timezone.utc)
    expired_tokens = [
        token
        for token, info in refresh_tokens.items()
        if info.exp < current_time or (sub and str(info.sub) == sub)
    ]

    for token in expired_tokens:
        del refresh_tokens[token]
