from app.models import UserModel

USERS: dict[int, UserModel] = {
    1: UserModel(
        username="admin",
        password="$5$rounds=535000$bb6X/mXPSDUHOI2Z$.PKsitB2aLIcIvQU.P5BK5Y9eo08TLJCLrNzye3U.o0",
    ),
}


def get_user_id(username: str) -> int | None:
    for id_, user in USERS.items():
        if user.username == username:
            return id_
    return None
