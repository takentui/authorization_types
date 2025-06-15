from fastapi import HTTPException, status
import secrets
from typing import Dict

from app.config import settings


def validate_credentials(username: str, password: str) -> bool:
    """Validate user credentials.

    Using secrets.compare_digest() instead of regular string comparison (==)
    provides protection against timing attacks. A timing attack is where
    an attacker measures the time it takes to compare strings to determine
    if they're getting closer to the correct value. The secrets module ensures
    that the comparison takes the same amount of time regardless of how many
    characters match, making the comparison resistant to timing attacks.
    """
    return secrets.compare_digest(
        username, settings.API_USERNAME
    ) and secrets.compare_digest(password, settings.API_PASSWORD)
