from pydantic import BaseModel


class ErrorMessage(BaseModel):
    """Error message model."""
    detail: str


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    username: str
    message: str = "Login successful"
