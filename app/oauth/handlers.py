from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from typing import Optional

from app.oauth.github import GitHubOAuth
from app.oauth.models import GitHubAuthURL, OAuthLoginResponse, OAuthUser
from app.database.users import create_or_update_oauth_user, get_oauth_user_by_username
from app.auth import create_token_pair, get_current_user
from app.models import ErrorMessage

router = APIRouter(prefix="/auth", tags=["OAuth"])

# Initialize GitHub OAuth client
try:
    github_oauth = GitHubOAuth()
except ValueError:
    github_oauth = None


@router.get(
    "/github",
    response_model=GitHubAuthURL,
    summary="Initialize GitHub OAuth",
    description="Get GitHub OAuth authorization URL",
    responses={
        200: {"description": "Authorization URL generated"},
        503: {"model": ErrorMessage, "description": "GitHub OAuth not configured"},
    },
)
async def github_login():
    """Initialize GitHub OAuth flow."""
    if not github_oauth:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET",
        )

    auth_url = github_oauth.get_authorization_url()
    return GitHubAuthURL(auth_url=auth_url)


@router.get(
    "/github/redirect",
    summary="GitHub OAuth redirect",
    description="Redirect to GitHub OAuth authorization",
)
async def github_redirect():
    """Direct redirect to GitHub OAuth (alternative to JSON response)."""
    if not github_oauth:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth not configured",
        )

    auth_url = github_oauth.get_authorization_url()
    return RedirectResponse(url=auth_url)


@router.get(
    "/github/callback",
    response_model=OAuthLoginResponse,
    summary="GitHub OAuth callback",
    description="Handle GitHub OAuth callback and create JWT tokens",
    responses={
        200: {"description": "OAuth login successful"},
        400: {"model": ErrorMessage, "description": "OAuth error"},
        502: {"model": ErrorMessage, "description": "GitHub API error"},
        503: {"model": ErrorMessage, "description": "GitHub OAuth not configured"},
    },
)
async def github_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    state: Optional[str] = None,
):
    """Handle GitHub OAuth callback."""
    if not github_oauth:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth not configured",
        )

    # Check for OAuth errors
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub OAuth error: {error_description or error}",
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided",
        )

    try:
        # Exchange code for access token
        token_response = await github_oauth.exchange_code_for_token(code, state)

        # Get user info from GitHub
        github_user = await github_oauth.get_user_info(token_response.access_token)

        # Get user emails (optional)
        try:
            emails = await github_oauth.get_user_emails(token_response.access_token)
            primary_email = None
            for email_info in emails:
                if email_info.get("primary"):
                    primary_email = email_info.get("email")
                    break
            if primary_email:
                github_user.email = primary_email
        except Exception:
            # Email access is optional, continue without it
            pass

        # Create or update OAuth user
        oauth_user = create_or_update_oauth_user(github_user.dict())

        # Create JWT tokens
        access_token, refresh_token = create_token_pair(oauth_user.username)

        return OAuthLoginResponse(
            access_token=access_token, refresh_token=refresh_token, user=oauth_user
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth process failed: {str(e)}",
        )


@router.get(
    "/user",
    response_model=OAuthUser,
    summary="Get OAuth user info",
    description="Get current OAuth user information",
    responses={
        200: {"description": "User information"},
        401: {"model": ErrorMessage, "description": "Unauthorized"},
        404: {"model": ErrorMessage, "description": "OAuth user not found"},
    },
)
async def get_oauth_user(username: str = Depends(get_current_user)):
    """Get current OAuth user information."""
    oauth_user = get_oauth_user_by_username(username)

    if not oauth_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OAuth user not found. This endpoint is only for OAuth-authenticated users.",
        )

    return oauth_user
