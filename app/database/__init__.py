from .local_db import LocalDatabase
from .models import User, Session

# Initialize database instance
db = LocalDatabase()

__all__ = ["LocalDatabase", "User", "Session", "db"]
