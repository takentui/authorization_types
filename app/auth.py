from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from app.config import settings

# Simple in-memory token blacklist store
# In production, use Redis or a database
blacklisted_tokens: Dict[str, datetime] = {}

# JWT Security
security = HTTPBearer()

# Global secret key to ensure consistency
_jwt_secret_key: Optional[str] = None

def get_jwt_secret_key() -> str:
    """Get JWT secret key from settings or generate a consistent one."""
    global _jwt_secret_key
    
    # First, try to get from settings
    if hasattr(settings, 'JWT_SECRET_KEY') and settings.JWT_SECRET_KEY:
        return settings.JWT_SECRET_KEY
    
    # If not in settings, generate once and store globally
    if _jwt_secret_key is None:
        _jwt_secret_key = secrets.token_urlsafe(32)
        print(f"Generated JWT secret key: {_jwt_secret_key}")  # For debugging
    
    return _jwt_secret_key

def validate_credentials(username: str, password: str) -> bool:
    """Validate user credentials.
    
    Using secrets.compare_digest() instead of regular string comparison (==)
    provides protection against timing attacks. A timing attack is where
    an attacker measures the time it takes to compare strings to determine
    if they're getting closer to the correct value. The secrets module ensures
    that the comparison takes the same amount of time regardless of how many
    characters match, making the comparison resistant to timing attacks.
    """
    return (secrets.compare_digest(username, settings.API_USERNAME) and 
            secrets.compare_digest(password, settings.API_PASSWORD))

def create_jwt_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token for the user."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    payload = {
        "sub": username,  # Subject (user identifier)
        "exp": int(expire.timestamp()),    # Expiration time as Unix timestamp
        "iat": int(datetime.now(timezone.utc).timestamp()),  # Issued at as Unix timestamp
        "jti": secrets.token_urlsafe(16)    # JWT ID (unique identifier)
    }
    
    return jwt.encode(payload, get_jwt_secret_key(), algorithm="HS256")

def decode_jwt_token(token: str) -> Dict:
    """Decode and validate a JWT token."""
    try:
        # Check if token is blacklisted
        if token in blacklisted_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        # Decode the token
        payload = jwt.decode(token, get_jwt_secret_key(), algorithms=["HS256"])
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract and validate the current user from JWT token."""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    username = payload.get("sub")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return username

def blacklist_token(token: str) -> None:
    """Add token to blacklist (for logout functionality)."""
    try:
        payload = jwt.decode(token, get_jwt_secret_key(), algorithms=["HS256"])
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
        token for token, exp_time in blacklisted_tokens.items()
        if exp_time < current_time
    ]
    
    for token in expired_tokens:
        del blacklisted_tokens[token] 