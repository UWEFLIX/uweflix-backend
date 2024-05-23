from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator
from src.schema.accounts import Account
from src.schema.films import ScheduleDetailed
from src.schema.validation import basic_string_validation


class PersonType(BaseModel):
    id: int
    person_type: str
    discount_amount: int = Field(ge=0, le=100)
    class_name: str = "PERSON_TYPE"

    @classmethod
    @field_validator("person_type", mode="before")
    def person_type_validation(cls, value: str):
        return basic_string_validation(value, "person_type")


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
    class_name: str = "BOOKING"

    @classmethod
    @field_validator("seat_no", mode="before")
    def seat_no_validation(cls, value: str):
        return basic_string_validation(value, "seat_no")

    @classmethod
    @field_validator("status", mode="before")
    def status_validation(cls, value: str):
        return basic_string_validation(value, "status")


class SingleBooking(BaseModel):
    seat_no: str
    schedule: ScheduleDetailed
    person_type: PersonType
    user_email: EmailStr
    account: Account
    class_name: str = "SINGLE_BOOKING"

    @classmethod
    @field_validator("seat_no", mode="before")
    def seat_no_validation(cls, value: str):
        return basic_string_validation(value, "seat_no")


class MultipleBookings(BaseModel):
    bookings: List[SingleBooking]
    club_id: int
    schedule_id: int
    account_id: int
    class_name: str = "MULTIPLE_BOOKINGS"


class BatchData(BaseModel):
    batch_ref: str
    count: int
    created: datetime
    total: int | float
    class_name: str = "BATCH_DATA"

