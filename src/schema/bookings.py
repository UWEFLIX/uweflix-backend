from src.schema.accounts import Account
from src.schema.films import ScheduleDetailed

from typing import List, Annotated
from datetime import datetime
from pydantic import (
    BaseModel, Field, EmailStr, field_validator, PlainSerializer, WrapValidator,
    WithJsonSchema
)
from typing_extensions import Doc
from src.schema.validation import basic_string_validation

_SEAT_NO_MAX_LENGTH = 7
# SEAT_NO_DELIMITER = "#"


def _seat_no_validation(value: str, handler) -> str:
    """
    todo update
    Validates a seat number string.

    - Must contain a set delimiter.
    - The length must not exceed set length characters.
    - The part before the delimiter must be alphabetic.
    - The part after the delimiter must be numeric.
    """
    if not isinstance(value, str):
        raise TypeError('string required')

    if len(value) > _SEAT_NO_MAX_LENGTH:
        raise ValueError("Length cannot be greater than 7 characters")

    value = value.upper()
    if not value.isalnum():
        raise ValueError("Not a valid seat number")

    row_alph = ""
    col_alph = ""
    for char in value:
        if char.isalpha():
            row_alph += char
        elif char.isnumeric():
            col_alph += char
        elif char.isspace():
            raise ValueError("Whitespace in string")
        else:
            raise ValueError("Invalid characters in seat")

    if not (row_alph.isalpha() and col_alph.isnumeric()):
        raise ValueError("Not a valid seat number")

    try:
        col = int(col_alph)
    except ValueError:
        raise ValueError("Invalid characters in seat")

    if 0 > col:
        raise ValueError("Seat column cannot be negative")

    return f"{row_alph}{col_alph}"


SeatNoStr = Annotated[
    str,
    WrapValidator(_seat_no_validation),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization')
]


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
    seat_no: SeatNoStr
    schedule: ScheduleDetailed
    status: str
    account: Account | None
    person_type: PersonType
    amount: float
    serial_no: str
    batch_ref: str
    created: datetime
    assigned_user: int
    class_name: str = "BOOKING"

    @classmethod
    @field_validator("status", mode="before")
    def status_validation(cls, value: str):
        return basic_string_validation(value, "status")


class _BookPerson(BaseModel):
    seat_no: SeatNoStr
    person_type_id: int
    user_id: int


class SingleBooking(BaseModel):
    person: _BookPerson
    schedule_id: int
    account_id: int
    class_name: str = "SINGLE_BOOKING"


class MultipleBookings(BaseModel):
    bookings: List[_BookPerson]
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


class Reporting(BaseModel):
    count: int = 0
    amount: float = 0
    class_name: str = "Reporting"


class SeatLock(BaseModel):
    id: int
    seat: SeatNoStr
    schedule_id: int
    is_manually_closed: bool
    created_at: datetime
    user_id: int
