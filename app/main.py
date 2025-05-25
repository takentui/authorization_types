from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials


from app.auth import (
    get_current_user,
    create_token_pair,
    blacklist_token,
    validate_credentials,
    security,
    validate_refresh_token,
    revoke_refresh_token,
    create_jwt_token,
)
from app.config import settings
from app.models import (
    ErrorMessage,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)

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
    # Validate credentials
    if not validate_credentials(login_request.username, login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create both access and refresh tokens
    access_token, refresh_token = create_token_pair(login_request.username)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        username=login_request.username,
    )


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
async def refresh_token(refresh_request: RefreshTokenRequest):
    """Refresh endpoint that generates a new access token using a refresh token."""
    # Validate refresh token and get username
    username = validate_refresh_token(refresh_request.refresh_token)

    # Create new access token
    new_access_token = create_jwt_token(username)

    return RefreshTokenResponse(access_token=new_access_token)


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
    refresh_request: RefreshTokenRequest = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Logout endpoint that blacklists the current JWT token and optionally revokes refresh token."""
    access_token = credentials.credentials
    blacklist_token(access_token)

    # If refresh token provided, revoke it
    if refresh_request and refresh_request.refresh_token:
        revoke_refresh_token(refresh_request.refresh_token)

    return {"message": "Logout successful"}


@app.get(
    "/me",
    summary="Get current user info",
    description="Get information about the currently authenticated user",
    responses={
        200: {"description": "User information"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def get_user_info(username: str = Depends(get_current_user)):
    """Get current user information from JWT token."""
    return {"username": username, "message": "User information retrieved successfully"}
