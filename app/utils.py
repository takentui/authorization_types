from app.config import settings


def get_ttl(is_remembered: bool) -> int:
    return (
        settings.MAX_COOKIE_AGE_REMEMBER
        if is_remembered
        else settings.MAX_COOKIE_AGE_DEFAULT
    )
