from typing import List, Set
from pydantic import BaseModel, Field, EmailStr, field_validator
from src.schema.validation import basic_string_validation


class Permission(BaseModel):
    id: int
    name: str
    class_name: str = "PERMISSION"

    def __repr__(self):
        return f"[id: {self.id}, name: {self.name}]"

    @classmethod
    @field_validator("name", mode="before")
    def name_validation(cls, value: str):
        return basic_string_validation(value, "name")


class Role(BaseModel):
    id: int
    name: str
    permissions: List[Permission]
    class_name: str = "ROLE"

    def __repr__(self):
        return (
            f"[id: {self.id}, name: {self.name}, permissions: "
            f"{self.permissions}]"
        )

    @classmethod
    @field_validator("name", mode="before")
    def name_validation(cls, value: str):
        return basic_string_validation(value, "name")


class User(BaseModel):
    id: int = Field(default=None, ge=0)
    name: str
    email: EmailStr
    password: str | None = Field(exclude=True, default=None)
    roles: List[Role] | None = Field(default=None)
    permissions: Set[str] | None = Field(default=None, exclude=True)
    status: str
    class_name: str = "USER"

    def __repr__(self):
        return (
            f"[id: {self.id}, name: {self.name}, email: {self.email},"
            f" roles: f{self.roles}, permissions: {self.permissions}]"
        )

    @classmethod
    @field_validator("name", mode="before")
    def name_validation(cls, value: str):
        return basic_string_validation(value, "name")

    @classmethod
    @field_validator("status", mode="before")
    def status_validation(cls, value: str):
        return basic_string_validation(value, "status")


class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    class_name: str = "PASSWORD_CHANGE"

    @classmethod
    @field_validator("old_password", mode="before")
    def old_password_validation(cls, value: str):
        return basic_string_validation(value, "old_password")

    @classmethod
    @field_validator("new_password", mode="before")
    def new_password_validation(cls, value: str):
        return basic_string_validation(value, "new_password")


class ResetRequest(BaseModel):
    email: EmailStr
    otp: str
    class_name: str = "RESET_REQUEST"

    @classmethod
    @field_validator("otp", mode="before")
    def otp_validation(cls, value: str):
        return basic_string_validation(value, "otp")


class PasswordResetConfirmation(ResetRequest):
    new_password: str
    class_name: str = "PASSWORD_RESET_CONFIRMATION"

    @classmethod
    @field_validator("new_password", mode="before")
    def new_password_validation(cls, value: str):
        return basic_string_validation(value, "new_password")
