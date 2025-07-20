from pydantic import BaseModel


class ErrorMessage(BaseModel):
    """Error message model."""

    detail: str


class LoginRequest(BaseModel):
    """Login request model."""

    username: str
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    """Login response model."""

    username: str
    message: str = "Login successful"


class UserModel(BaseModel):
    username: str
    password: str


class ActiveSessionModel(BaseModel):
    user_id: int
    expired: int
    remember_me: bool
