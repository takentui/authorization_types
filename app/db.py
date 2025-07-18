from pydantic import BaseModel


class ObjectModel(BaseModel):
    field1: str
    field2: int


class DBObjectModel(ObjectModel):
    username: str


USERS: dict[str, str] = {
    "admin": "$5$rounds=535000$0IzpLdaBMPEnQezO$M4jAk/ayl3H6ZHDlojv3EqDUAJy3.5Py3wpYNOFXVQ5",
    "kek": "$5$rounds=535000$a1MD64jYLZTonMR7$E4YG4UGV5erLKltSMyUrNj7V9xUNkuIGhwA0Dg1WCRB",
    "mazda": "$5$rounds=535000$XXEaIhBmqChyw8i5$JMKpzzOMYtjA1W6WZBqJBOdx6XlTHe9clDjRahac261",
}

OBJECTS: dict[int, DBObjectModel] = {}
