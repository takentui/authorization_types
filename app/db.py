from pydantic import BaseModel


class UserModel(BaseModel):
    username: str
    roles: list[str]


class UserFullModel(UserModel):
    password_hash: str


users: dict[int, UserFullModel] = {
    0: UserFullModel(
        username="admin",
        password_hash="$5$rounds=535000$VmjDekF0Mi38FSlc$KF6JKT1wXEZCw7rB/zK3om/4Bo.Vuf74mLRHQuYiEh0",
        roles=["admin"],
    )
}
