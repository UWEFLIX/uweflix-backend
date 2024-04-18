from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class Hall(BaseModel):
    id: int
    hall_name: str
    seats_per_row: int = Field(..., ge=1)
    no_of_rows: int = Field(..., ge=1)


class FilmImage(BaseModel):
    id: int
    filename: str


class Schedule(BaseModel):
    id: int
    hall_id: int
    film_id: int
    show_time: datetime
    on_schedule: bool
    ticket_price: float = Field(..., ge=1)


class Film(BaseModel):
    id: int
    title: str
    age_rating: str
    duration_sec: int = Field(..., ge=1)
    trailer_desc: str
    on_air_from: datetime
    on_air_to: datetime
    is_active: bool
    poster_image: bytes | None = None
    images: List[FilmImage] | None = None
    schedules: List[Schedule] | None = None


class ScheduleDetailed(Schedule):
    hall: Hall | None = None
    film: Film | None = None