from pydantic import BaseModel


class Hall(BaseModel):
    id: int | None = None
    hall_name: str
    seats_per_row: int
    no_of_rows: int
