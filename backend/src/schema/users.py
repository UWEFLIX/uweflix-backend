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


class Card(BaseModel):
    id: int | None
    account_id: int | None
    card_number: int
    holder_name: str
    exp_date: str = Field(max_length=5)
    status: str


class Account(BaseModel):
    id: int | None
    uid: str
    name: str
    cards: List[Card] | None
    entity_type: str
    discount_rate: int = Field(min_value=0, max_value=100)


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
