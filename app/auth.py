from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

# Initialize HTTP Basic security
security = HTTPBasic()

# Hardcoded credentials for demo purposes
# In a real application, use environment variables or secure storage
USERNAME = os.getenv("API_USERNAME", "admin")
PASSWORD = os.getenv("API_PASSWORD", "password")

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Dependency to validate basic auth credentials.
    
    Returns username on success, raises 401 exception on failure.
    """
    is_correct_username = secrets.compare_digest(credentials.username, USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username 