from fastapi import HTTPException, status, Cookie, Response
import secrets
import string
from typing import Optional, Dict

from app.config import settings

# Simple in-memory session store
# In production, use Redis or a database
active_sessions: Dict[str, str] = {}

def get_random_session_token(length: int = 32) -> str:
    """Generate a random session token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

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

def create_session(username: str, response: Response) -> str:
    """Create a new session for the user and set the session cookie."""
    session_token = get_random_session_token()
    active_sessions[session_token] = username
    
    # Set the session cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,  # Prevent JavaScript access
        max_age=1800,   # 30 minutes
        # secure=True,  # Uncomment in production (HTTPS only)
        samesite="lax"  # Prevent CSRF
    )
    
    return session_token

def get_current_user_from_cookie(
    session_token: Optional[str] = Cookie(None)
) -> str:
    """Validate the session token from cookie."""
    if session_token is None or session_token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session or session expired",
        )
    
    return active_sessions[session_token]

def end_session(session_token: str, response: Response) -> None:
    """End a user session and clear the cookie."""
    if session_token in active_sessions:
        del active_sessions[session_token]
    
    response.delete_cookie(key="session_token") 