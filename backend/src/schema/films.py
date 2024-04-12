from datetime import datetime
from typing import List

from fastapi import UploadFile
from pydantic import BaseModel
from starlette.responses import FileResponse


class Hall(BaseModel):
    id: int
    hall_name: str
    seats_per_row: int
    no_of_rows: int


class FilmImage(BaseModel):
    id: int
    filename: str


class Film(BaseModel):
    id: int
    title: str
    age_rating: str
    duration_sec: int
    trailer_desc: str
    on_air_from: datetime
    on_air_to: datetime
    is_active: bool
    poster_image: bytes | None = None
    images: List[FilmImage] | None = None


class Schedule(BaseModel):
    id: int
    hall: Hall | None = None
    film: Film | None = None
    showtime: datetime
    on_schedule: bool
    ticket_price: float
