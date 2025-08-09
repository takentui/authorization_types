import datetime

from pydantic import BaseModel, UUID4


class ErrorMessage(BaseModel):
    """Error message model."""

    detail: str


class LoginRequest(BaseModel):
    """Login request model."""

    username: str
    password: str
    is_remember_me: bool = False


class LoginResponse(BaseModel):
    """Login response model with both access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    username: str
    message: str = "Login successful"


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response model with new access token."""

    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    message: str = "Token refreshed successfully"


class RegistrationRequest(BaseModel):
    """Register request model."""

    username: str
    password: str
    roles: list[str]
    is_remember_me: bool = False


class RefreshTokenInfo(BaseModel):
    sub: UUID4
    exp: datetime.datetime
    is_remember_me: bool
