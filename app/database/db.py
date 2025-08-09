from pydantic import BaseModel, UUID4


class UserModel(BaseModel):
    uid: UUID4
    username: str
    roles: list[str]


class UserFullModel(UserModel):
    password_hash: str


DB_USERS: dict[str, UserFullModel] = {}
