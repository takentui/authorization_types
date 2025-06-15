import logging
from datetime import datetime

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import db
from app.keycloak.client import keycloak_client

logger = logging.getLogger(__name__)

# Keycloak HTTP Bearer security
keycloak_security = HTTPBearer()


def get_current_user_keycloak(
    credentials: HTTPAuthorizationCredentials = Depends(keycloak_security),
) -> str:
    """Extract and validate the current user from Keycloak token."""
    token = credentials.credentials

    try:
        # Validate token with Keycloak
        userinfo = keycloak_client.validate_token(token)
        username = userinfo.get("preferred_username")

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        # Optionally cache user profile (not required for auth)
        if not db.exists("users", username):
            user_data = {
                "username": username,
                "email": userinfo.get("email", ""),
                "keycloak_id": userinfo.get("sub", ""),
                "roles": userinfo.get("realm_access", {}).get("roles", []),
                "created_at": datetime.now().isoformat(),
            }
            db.set("users", username, user_data)

        # Reject black-listed tokens (logout)
        if db.exists("blacklist", token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        return username

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )


class KeycloakHTTPBearer(HTTPBearer):
    """Custom HTTP Bearer for Keycloak authentication."""

    async def __call__(self, request) -> HTTPAuthorizationCredentials:
        credentials = await super().__call__(request)

        # Additional validation can be added here
        return credentials
