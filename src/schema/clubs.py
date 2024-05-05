from typing import List

from pydantic import BaseModel, EmailStr

from src.schema.users import User


class City(BaseModel):
    id: int
    name: str


class Club(BaseModel):
    id: int
    leader: User | None
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
