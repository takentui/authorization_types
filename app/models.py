from pydantic import BaseModel


class ErrorMessage(BaseModel):
    error: str
    detail: str | None = None
