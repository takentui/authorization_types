from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import (
    get_current_user,
    create_jwt_token,
    blacklist_token,
    security,
    create_jwt_token_unsigned,
    get_current_user_unsign,
    get_user_by_role,
)
from app.config import settings
from app.db import users, UserFullModel, UserModel
from app.models import ErrorMessage, LoginRequest, AccessTokenResponse, RegisterRequest
from app.service import register_user, get_user_by_credentials

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


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the FastAPI JWT Auth Example"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/public")
async def public_route():
    """Example public route accessible without authentication."""
    return {"message": "This is a public route", "data": "public information"}


@app.post(
    "/login",
    response_model=AccessTokenResponse,
    summary="Login with username and password",
    description="Get a JWT access token",
    responses={
        200: {"description": "Login successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid credentials",
        },
    },
)
async def login(login_request: LoginRequest):
    """Login endpoint that returns a JWT access token."""
    # Validate credentials
    user = get_user_by_credentials(login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create JWT token
    access_token = create_jwt_token(user, login_request.is_remember_me)

    return AccessTokenResponse(
        access_token=access_token, username=login_request.username
    )


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
async def protected_route(username: str = Depends(get_current_user_unsign)):
    """Protected route that requires a valid JWT token."""
    return {
        "message": "This is a protected route",
        "data": "secret information accessible with JWT token",
        "authenticated_user": username,
    }


@app.post(
    "/logout",
    summary="Logout and blacklist token",
    description="Blacklist the current JWT token to prevent further use",
    responses={
        200: {"description": "Logout successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout endpoint that blacklists the current JWT token."""
    token = credentials.credentials
    blacklist_token(token)

    return {"message": "Logout successful"}


@app.get(
    "/me",
    summary="Get current user info",
    response_model=UserModel,
    description="Get information about the currently authenticated user",
    responses={
        200: {"description": "User information"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def get_user_info(user: UserModel = Depends(get_current_user)):
    """Get current user information from JWT token."""
    return user


@app.post(
    "/login/unsigned",
    response_model=AccessTokenResponse,
    summary="Login with username and password",
    description="Get an unsigned JWT access token",
    responses={
        200: {"description": "Login successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid credentials",
        },
    },
)
async def login_unsigned(login_request: LoginRequest):
    """Login endpoint that returns a JWT access token."""
    # Validate credentials
    if not get_user_by_credentials(login_request.username, login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create JWT token
    access_token = create_jwt_token_unsigned(login_request.username)

    return AccessTokenResponse(
        access_token=access_token, username=login_request.username
    )


@app.post(
    "/users",
    response_model=AccessTokenResponse,
    summary="Register new user with username and password",
    description="Register new user and get a JWT access token",
    responses={
        200: {"description": "Register successful"},
    },
)
async def register(register_request: RegisterRequest):
    """Login endpoint that returns a JWT access token."""

    user = await register_user(register_request)
    # Create JWT token
    access_token = create_jwt_token(user, is_remember_me=False)

    return AccessTokenResponse(access_token=access_token, username=user.username)


@app.get(
    "/admin",
    summary="Get admin info",
    description="Get information about the currently authenticated user",
    responses={
        200: {"description": "User information"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
    dependencies=[Depends(get_user_by_role("admin"))],
)
async def get_admin_info():
    return {"message": "It's for admin only!"}
