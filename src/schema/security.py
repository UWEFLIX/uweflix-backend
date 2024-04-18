from typing import List
from pydantic import BaseModel


class TokenData(BaseModel):
    username: str | None = None
    password: str | None = None
    scopes: List[str] = []


class Token(BaseModel):
    access_token: str
    token_type: str

