from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime

from app.keycloak import get_current_user_keycloak, keycloak_client
from app.keycloak.auth import keycloak_security
from app.database import db
from app.config import settings
from app.models import (
    ErrorMessage,
    LoginRequest,
    LoginResponse,
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
    return {"message": "Welcome to the FastAPI Keycloak Auth Example"}


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
    description="Get Keycloak access token",
    responses={
        200: {"description": "Login successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid credentials",
        },
    },
)
async def login(login_request: LoginRequest):
    """Login endpoint that returns Keycloak access token."""
    try:
        # Authenticate with Keycloak
        token_response = keycloak_client.authenticate_user(
            login_request.username, login_request.password
        )

        return LoginResponse(
            access_token=token_response["access_token"],
            username=login_request.username,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error",
        )


@app.get(
    "/protected",
    summary="Protected route (requires Keycloak token)",
    description="This endpoint requires a valid Keycloak token in Authorization header",
    responses={
        200: {"description": "Successful response"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def protected_route(username: str = Depends(get_current_user_keycloak)):
    """Protected route that requires a valid Keycloak token."""
    return {
        "message": "This is a protected route",
        "data": "secret information accessible with Keycloak token",
        "authenticated_user": username,
    }


@app.post(
    "/logout",
    summary="Logout and blacklist token",
    description="Invalidate current access token by adding it to local blacklist",
    responses={
        200: {"description": "Logout successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(keycloak_security),
    username: str = Depends(get_current_user_keycloak),
):
    """Logout endpoint that blacklists current access token."""
    token = credentials.credentials
    db.set(
        "blacklist",
        token,
        {"username": username, "revoked_at": datetime.now().isoformat()},
    )
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
async def get_user_info(username: str = Depends(get_current_user_keycloak)):
    """Get current user information from local database."""
    user_data = db.get("users", username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {
        "username": username,
        "user_data": user_data,
        "message": "User information retrieved successfully",
    }
