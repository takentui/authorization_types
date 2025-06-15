from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ErrorMessage(BaseModel):
    """Error message model."""

    detail: str


class LoginRequest(BaseModel):
    """Login request model."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model with access token."""

    access_token: str
    token_type: str = "bearer"
    username: str
    message: str = "Login successful"


class KeycloakUser(BaseModel):
    """Keycloak user model."""

    keycloak_id: str
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = []
    enabled: bool = True


class KeycloakTokenResponse(BaseModel):
    """Keycloak token response model."""

    access_token: str
    expires_in: int
    refresh_expires_in: int
    token_type: str
    not_before_policy: int
    scope: str
