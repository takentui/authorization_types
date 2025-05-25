from pydantic import BaseModel


class ErrorMessage(BaseModel):
    """Error message model."""

    detail: str


class LoginRequest(BaseModel):
    """Login request model."""

    username: str
    password: str


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
    message: str = "Token refreshed successfully"
