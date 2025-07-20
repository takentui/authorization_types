import logging.config

from fastapi import FastAPI, Depends, Response, Cookie, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.auth import (
    get_current_user_from_cookie,
    create_session,
    end_session,
    validate_credentials,
    create_user,
)
from app.config import settings
from app.db import USERS
from app.logger import LOGGING_CONFIG
from app.models import ErrorMessage, LoginRequest, LoginResponse

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


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the FastAPI Session Auth Example"}


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
    description="Create a session and set a cookie",
    responses={
        200: {"description": "Login successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid credentials",
        },
    },
)
async def login(login_request: LoginRequest, response: Response):
    """Login endpoint that creates a session and sets a cookie."""
    # Validate credentials
    if not validate_credentials(login_request.username, login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create session and set cookie
    create_session(login_request, response)

    return LoginResponse(username=login_request.username)


@app.post(
    "/registration",
    response_model=LoginResponse,
    description="Register a new user and create a session and set a cookie",
    responses={
        200: {"description": "User created successful"},
        400: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid credentials",
        },
    },
)
async def register(login_request: LoginRequest, response: Response):
    """Register endpoint that creates a new user and a session and sets a cookie."""
    user = create_user(login_request.username, login_request.password)

    # Create session and set cookie
    create_session(login_request, response)

    return LoginResponse(username=login_request.username)


@app.get(
    "/protected",
    summary="Protected route (requires session cookie)",
    description="This endpoint requires a valid session cookie to access",
    responses={
        200: {"description": "Successful response"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing session",
        },
    },
)
async def protected_route(user_id: int = Depends(get_current_user_from_cookie)):
    """Protected route that requires a valid session cookie."""
    user = USERS[user_id]
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user"
        )

    return {
        "message": "This is a protected route",
        "data": "secret information accessible with cookie",
        "authenticated_user": user.username,
    }


@app.post(
    "/logout",
    summary="Logout and end session",
    description="End the current session and clear the session cookie",
    responses={
        200: {"description": "Logout successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing session",
        },
    },
)
async def logout(
    response: Response,
    session_token: Optional[str] = Cookie(None, alias="session_token"),
):
    """Logout endpoint that ends the session and clears the cookie."""
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No active session"
        )

    end_session(session_token, response)

    return {"message": "Logout successful"}
