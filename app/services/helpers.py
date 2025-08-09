import uuid

from pydantic import UUID4

from app.database.db import DB_USERS


def generate_user_uid() -> UUID4:
    while True:
        uid = uuid.uuid4()
        if uid not in DB_USERS:
            return uid
