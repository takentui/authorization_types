from typing import Dict, Optional
from datetime import datetime
from app.oauth.models import OAuthUser


# In-memory storage for OAuth users
# In production, use a real database
oauth_users: Dict[str, OAuthUser] = {}  # username -> OAuthUser
github_id_to_username: Dict[int, str] = {}  # github_id -> username


def create_or_update_oauth_user(github_user_data: dict) -> OAuthUser:
    """Create or update OAuth user from GitHub data."""
    github_id = github_user_data["id"]
    username = github_user_data["login"]

    # Check if user already exists by GitHub ID
    existing_username = github_id_to_username.get(github_id)
    if existing_username and existing_username in oauth_users:
        # Update existing user
        existing_user = oauth_users[existing_username]
        existing_user.display_name = github_user_data.get("name")
        existing_user.email = github_user_data.get("email")
        existing_user.avatar_url = github_user_data.get("avatar_url")
        existing_user.profile_url = github_user_data.get("html_url")
        existing_user.last_login = datetime.utcnow()
        return existing_user

    # Create new user
    oauth_user = OAuthUser(
        github_id=github_id,
        username=username,
        display_name=github_user_data.get("name"),
        email=github_user_data.get("email"),
        avatar_url=github_user_data.get("avatar_url"),
        profile_url=github_user_data.get("html_url"),
    )

    # Store user
    oauth_users[username] = oauth_user
    github_id_to_username[github_id] = username

    return oauth_user


def get_oauth_user_by_username(username: str) -> Optional[OAuthUser]:
    """Get OAuth user by username."""
    return oauth_users.get(username)


def get_oauth_user_by_github_id(github_id: int) -> Optional[OAuthUser]:
    """Get OAuth user by GitHub ID."""
    username = github_id_to_username.get(github_id)
    if username:
        return oauth_users.get(username)
    return None


def delete_oauth_user(username: str) -> bool:
    """Delete OAuth user."""
    if username in oauth_users:
        user = oauth_users[username]
        del oauth_users[username]
        # Remove from GitHub ID mapping
        if user.github_id in github_id_to_username:
            del github_id_to_username[user.github_id]
        return True
    return False


def clear_oauth_users() -> None:
    """Clear all OAuth users (for testing)."""
    oauth_users.clear()
    github_id_to_username.clear()
