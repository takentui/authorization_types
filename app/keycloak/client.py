from keycloak import KeycloakOpenID
from fastapi import HTTPException, status
from typing import Dict, Any, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class KeycloakClient:
    """Keycloak client for authentication operations."""

    def __init__(self):
        self.keycloak_openid = KeycloakOpenID(
            server_url=settings.KEYCLOAK_SERVER_URL,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            realm_name=settings.KEYCLOAK_REALM,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
        )

    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user with Keycloak and return token."""
        try:
            token = self.keycloak_openid.token(username, password)
            return token
        except Exception as e:
            logger.error(f"Keycloak authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate access token and return user info."""
        try:
            # Validate token and get user info
            userinfo = self.keycloak_openid.userinfo(token)
            return userinfo
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

    def get_user_info(self, token: str) -> Dict[str, Any]:
        """Get user information from token."""
        try:
            userinfo = self.keycloak_openid.userinfo(token)
            return userinfo
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to retrieve user information",
            )

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        try:
            token = self.keycloak_openid.refresh_token(refresh_token)
            return token
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

    def logout(self, refresh_token: str) -> None:
        """Logout user by invalidating refresh token."""
        try:
            self.keycloak_openid.logout(refresh_token)
        except Exception as e:
            logger.warning(f"Logout failed: {e}")
            # Don't raise exception for logout failures


# Global Keycloak client instance
keycloak_client = KeycloakClient()
