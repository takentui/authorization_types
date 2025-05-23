from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import get_current_user, create_jwt_token, blacklist_token, validate_credentials, security
from app.config import settings
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
    description="Get a JWT access token",
    responses={
        200: {"description": "Login successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid credentials"
        }
    }
)
async def login(login_request: LoginRequest):
    """Login endpoint that returns a JWT access token."""
    # Validate credentials
    if not validate_credentials(login_request.username, login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create JWT token
    access_token = create_jwt_token(login_request.username)
    
    return LoginResponse(
        access_token=access_token,
        username=login_request.username
    )


@app.get(
    "/protected",
    summary="Protected route (requires JWT token)",
    description="This endpoint requires a valid JWT token in Authorization header",
    responses={
        200: {"description": "Successful response"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token"
        }
    }
)
async def protected_route(username: str = Depends(get_current_user)):
    """Protected route that requires a valid JWT token."""
    return {
        "message": "This is a protected route",
        "data": "secret information accessible with JWT token",
        "authenticated_user": username
    }


@app.post(
    "/logout",
    summary="Logout and blacklist token",
    description="Blacklist the current JWT token to prevent further use",
    responses={
        200: {"description": "Logout successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token"
        }
    }
)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout endpoint that blacklists the current JWT token."""
    token = credentials.credentials
    blacklist_token(token)
    
    return {"message": "Logout successful"}


@app.get(
    "/me",
    summary="Get current user info",
    description="Get information about the currently authenticated user",
    responses={
        200: {"description": "User information"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token"
        }
    }
)
async def get_user_info(username: str = Depends(get_current_user)):
    """Get current user information from JWT token."""
    return {
        "username": username,
        "message": "User information retrieved successfully"
    }