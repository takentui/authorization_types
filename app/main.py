import logging.config

from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4

from app.config import settings, LOGGING_CONFIG
from app.database.db import UserModel
from app.models import (
    ErrorMessage,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegistrationRequest,
)
from app.services.auth import (
    get_current_user,
    blacklist_token,
    security,
    generate_refresh_token,
)
from app.services.business_logic import register_new_user, authorize, roles
from app.services.users import get_user

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.config.dictConfig(LOGGING_CONFIG)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post(
    "/login",
    response_model=LoginResponse,
    summary="Login with username and password",
    description="Get JWT access and refresh tokens",
    responses={
        200: {"description": "Login successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid credentials",
        },
    },
)
async def login(login_request: LoginRequest):
    """Login endpoint that returns both access and refresh tokens."""
    return jsonable_encoder(authorize(login_request))


@app.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or expired refresh token",
        },
    },
)
async def refresh_token_handler(refresh_request: RefreshTokenRequest):
    """Refresh endpoint that generates a new access token using a refresh token."""
    # Validate refresh token and get username
    return generate_refresh_token(refresh_request.refresh_token)


@app.get(
    "/protected",
    summary="Protected route (requires JWT token)",
    description="This endpoint requires a valid JWT token in Authorization header",
    responses={
        200: {"description": "Successful response"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def protected_route(username: str = Depends(get_current_user)):
    """Protected route that requires a valid JWT token."""
    return {
        "message": "This is a protected route",
        "data": "secret information accessible with JWT token",
        "authenticated_user": username,
    }


@app.post(
    "/logout",
    summary="Logout and blacklist tokens",
    description="Blacklist the current JWT token and optionally revoke refresh token",
    responses={
        200: {"description": "Logout successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Logout endpoint that blacklists the current JWT token and optionally revokes refresh token."""
    access_token = credentials.credentials
    blacklist_token(access_token)

    return {"message": "Logout successful"}


@app.get(
    "/me",
    summary="Get current user info",
    description="Get information about the currently authenticated user",
    response_model=UserModel,
    responses={
        200: {"description": "User information"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def get_user_info(user_uid: UUID4 = Depends(get_current_user)):
    """Get current user information from JWT token."""
    return jsonable_encoder(get_user(user_uid))


@app.post(
    "/registration",
    response_model=RefreshTokenResponse,
    summary="Register new user",
    description="Register new user and get a new access token",
    responses={
        201: {"description": "User registered successfully"},
    },
)
async def register_new_user_handler(
    request: RegistrationRequest,
) -> RefreshTokenResponse:
    """Register new user"""
    return jsonable_encoder(register_new_user(request))


@app.get(
    "/admin",
    summary="For admin only",
    responses={
        200: {"description": "User information"},
        403: {
            "model": ErrorMessage,
            "description": "Access forbidden",
        },
    },
)
@roles({"admin"})
async def admin_handler(user_uid: UUID4 = Depends(get_current_user)):
    return {"message": "It's for admin only!", "user_uid": user_uid}
