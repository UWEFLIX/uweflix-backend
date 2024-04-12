from pydantic import BaseModel, Field
from src.schema.accounts import Account
from src.schema.films import Schedule


class PersonType(BaseModel):
    id: int | None = None
    person_type: str
    discount_amount: int = Field(ge=0, le=100)


class Booking(BaseModel):
    id: int | None = None
    seat_no: str
    entity_type: str
    schedule: Schedule
    status: str
    account: Account
    person_type: PersonType
    amount: float
    serial_no: str
    batch_ref: str
