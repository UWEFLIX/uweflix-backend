from typing import List, Set

from pydantic import BaseModel, Field


class Permissions(BaseModel):
    id: int | None
    name: str

    def __repr__(self):
        return f"[id: {self.id}, name: {self.name}]"


class Role(BaseModel):
    id: int | None
    name: str
    permissions: List[Permissions]

    def __repr__(self):
        return f"[id: {self.id}, name: {self.name}, permissions: {self.permissions}]"


class User(BaseModel):
    id: int | None = None
    name: str
    password: str = Field(exclude=True)
    roles: List[Role] | None = None
    permissions: Set[str] | None = Field(default=None, exclude=True)

    def __repr__(self):
        return (
            f"[id: {self.id}, name: {self.name},"
            f" roles: f{self.roles}, permissions: {self.permissions}]"
        )
