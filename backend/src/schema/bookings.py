from pydantic import BaseModel, Field


class PersonType(BaseModel):
    id: int | None = None
    person_type: str
    discount_amount: int = Field(ge=1, le=100)
