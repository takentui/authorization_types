from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GitHubUser(BaseModel):
    """GitHub user model from OAuth."""

    id: int
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OAuthUser(BaseModel):
    """Internal OAuth user representation."""

    github_id: int
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None
    provider: str = "github"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)


class GitHubTokenResponse(BaseModel):
    """GitHub OAuth token response."""

    access_token: str
    token_type: str = "bearer"
    scope: str


class OAuthLoginResponse(BaseModel):
    """OAuth login response with JWT tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: OAuthUser
    message: str = "OAuth login successful"


class GitHubAuthURL(BaseModel):
    """GitHub authorization URL response."""

    auth_url: str
    state: Optional[str] = None
