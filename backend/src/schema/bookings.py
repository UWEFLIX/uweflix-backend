from pydantic import BaseModel, Field
from src.schema.accounts import Account
from src.schema.clubs import Club
from src.schema.films import Schedule, ScheduleDetailed
from src.schema.users import User


class PersonType(BaseModel):
    id: int
    person_type: str
    discount_amount: int = Field(ge=0, le=100)


class Booking(BaseModel):
    id: int
    seat_no: str
    entity_type: str
    entity_id: int
    schedule: ScheduleDetailed
    status: str
    account: Account
    person_type: PersonType
    amount: float
    serial_no: str
    batch_ref: str


class ClubBooking(Booking):
    club: Club


class IndividualBooking(Booking):
    user: User
