from typing import List

from pydantic import BaseModel, EmailStr, field_validator

from src.schema.users import User
from src.schema.validation import basic_string_validation


class City(BaseModel):
    id: int
    name: str

    @classmethod
    @field_validator("name", mode="before")
    def name_validation(cls, value: str):
        return basic_string_validation(value, "name")


class Club(BaseModel):
    id: int
    leader: User | None = None
    club_name: str
    addr_street_number: str
    addr_street_name: str
    email: EmailStr
    contact_number: str
    landline_number: str
    post_code: int
    city: City
    status: str

    members: List[User] | None = None

    @classmethod
    @field_validator("club_name", mode="before")
    def club_name_validation(cls, value: str):
        return basic_string_validation(value, "club_name")
