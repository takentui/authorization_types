from pydantic import BaseModel


class ErrorMessage(BaseModel):
    """Error message model."""

    detail: str


class LoginRequest(BaseModel):
    """Login request model."""

    username: str
    password: str
    is_remember_me: bool = False


class AccessTokenResponse(BaseModel):
    """Login response model."""

    access_token: str
    token_type: str = "bearer"
    username: str
    message: str = "Login successful"


class RegisterRequest(BaseModel):
    """Register request model."""

    username: str
    password: str
    roles: list[str]
