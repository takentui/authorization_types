from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth import get_current_user
from app.config import settings
from app.models import ErrorMessage

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
    return {"message": "Welcome to the FastAPI Basic Auth Example"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/public")
async def public_route():
    """Example public route accessible without authentication."""
    return {"message": "This is a public route", "data": "public information"}

@app.get(
    "/protected",
    summary="Protected route (requires authentication)",
    description="This endpoint requires Basic Authentication to access",
    responses={
        200: {"description": "Successful response"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid credentials"
        }
    }
)
async def protected_route(username: str = Depends(get_current_user)):
    """Protected route that requires basic authentication."""
    return {
        "message": "This is a protected route",
        "data": "secret information",
        "authenticated_user": username
    }