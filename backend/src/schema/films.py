from datetime import datetime
from typing import List

from fastapi import UploadFile
from pydantic import BaseModel


class Hall(BaseModel):
    id: int | None = None
    hall_name: str
    seats_per_row: int
    no_of_rows: int


class Film(BaseModel):
    id: int | None = None
    title: str
    age_rating: str
    duration_sec: int
    trailer_desc: str
    on_air_from: datetime
    on_air_to: datetime
    is_active: bool
    poster_image: UploadFile | None = None
    images: List[str] | None = None


class Schedule(BaseModel):
    id: int | None = None
    hall: Hall
    film: Film
    showtime: datetime
    on_schedule: bool
    ticket_price: float
