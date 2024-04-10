from typing import List, Set

from pydantic import BaseModel, Field, EmailStr


class Permission(BaseModel):
    id: int | None
    name: str

    def __repr__(self):
        return f"[id: {self.id}, name: {self.name}]"


class Role(BaseModel):
    id: int | None
    name: str
    permissions: List[Permission]

    def __repr__(self):
        return (
            f"[id: {self.id}, name: {self.name}, permissions: "
            f"{self.permissions}]"
        )


class User(BaseModel):
    id: int | None = Field(default=None, ge=0)
    name: str
    email: EmailStr
    password: str = Field(exclude=True)
    roles: List[Role] | None = Field(default=None)
    permissions: Set[str] | None = Field(default=None, exclude=True)
    status: str

    def __repr__(self):
        return (
            f"[id: {self.id}, name: {self.name}, email: {self.email},"
            f" roles: f{self.roles}, permissions: {self.permissions}]"
        )


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class ResetRequest(BaseModel):
    email: EmailStr
    otp: str


class PasswordResetConfirmation(ResetRequest):
    new_password: str
