from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from src.schema.accounts import Account
from src.schema.clubs import Club
from src.schema.films import ScheduleDetailed
from src.schema.users import User


class PersonType(BaseModel):
    id: int
    person_type: str
    discount_amount: int = Field(ge=0, le=100)


class Booking(BaseModel):
    id: int
    seat_no: str
    schedule: ScheduleDetailed
    status: str
    account: Account
    person_type: PersonType
    amount: float
    serial_no: str
    batch_ref: str
    created: datetime
    assigned_user: EmailStr


class SingleBooking(BaseModel):
    seat_no: str
    schedule: ScheduleDetailed
    person_type: PersonType
    user_email: EmailStr
    account: Account


class MultipleBookings(BaseModel):
    bookings: List[SingleBooking]
    club_id: int
    schedule_id: int
    account_id: int


class BatchData(BaseModel):
    batch_ref: str
    count: int
    created: datetime
    total: float
