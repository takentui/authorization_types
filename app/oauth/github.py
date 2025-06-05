import httpx
import secrets
from urllib.parse import urlencode
from typing import Dict, Optional
from fastapi import HTTPException, status

from app.config import settings
from app.oauth.models import GitHubUser, GitHubTokenResponse


class GitHubOAuth:
    """GitHub OAuth 2.0 client."""

    def __init__(self):
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            raise ValueError("GitHub OAuth credentials not configured")

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate GitHub OAuth authorization URL."""
        if state is None:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "scope": settings.GITHUB_SCOPE,
            "state": state,
            "response_type": "code",
        }

        return f"{settings.GITHUB_AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_token(
        self, code: str, state: Optional[str] = None
    ) -> GitHubTokenResponse:
        """Exchange authorization code for access token."""
        data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
        }

        headers = {"Accept": "application/json", "User-Agent": "FastAPI-OAuth-App"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    settings.GITHUB_TOKEN_URL, data=data, headers=headers, timeout=30.0
                )
                response.raise_for_status()

                token_data = response.json()

                if "error" in token_data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"GitHub OAuth error: {token_data.get('error_description', 'Unknown error')}",
                    )

                return GitHubTokenResponse(**token_data)

            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to exchange code for token: {str(e)}",
                )

    async def get_user_info(self, access_token: str) -> GitHubUser:
        """Get user information from GitHub API."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "FastAPI-OAuth-App",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    settings.GITHUB_USER_URL, headers=headers, timeout=30.0
                )
                response.raise_for_status()

                user_data = response.json()
                return GitHubUser(**user_data)

            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to get user info: {str(e)}",
                )

    async def get_user_emails(self, access_token: str) -> list:
        """Get user email addresses from GitHub API."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "FastAPI-OAuth-App",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.GITHUB_USER_URL}/emails", headers=headers, timeout=30.0
                )
                response.raise_for_status()

                return response.json()

            except httpx.HTTPError:
                # Email access is optional
                return []
