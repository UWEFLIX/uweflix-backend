from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator

from src.schema.validation import basic_string_validation


class Hall(BaseModel):
    id: int
    hall_name: str
    seats_per_row: int = Field(..., ge=1)
    no_of_rows: int = Field(..., ge=1)

    @classmethod
    @field_validator("hall_name", mode="before")
    def hall_name_validation(cls, value: str):
        return basic_string_validation(value, "hall_name")


class FilmImage(BaseModel):
    id: int
    filename: str

    @classmethod
    @field_validator("filename", mode="before")
    def filename_validation(cls, value: str):
        new_value = basic_string_validation(value, "filename")
        if "\\" in new_value or "/" in new_value:
            raise ValueError("Invalid characters in filename")
        return new_value


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
    on_air_from: datetime | str
    on_air_to: datetime | str
    is_active: bool
    poster_image: bytes | None = None
    images: List[FilmImage] | None = None
    schedules: List[Schedule] | None = None

    @classmethod
    @field_validator("title", mode="before")
    def title_validation(cls, value: str):
        return basic_string_validation(value, "title")

    @classmethod
    @field_validator("age_rating", mode="before")
    def age_rating_validation(cls, value: str):
        return basic_string_validation(value, "age_rating")


class ScheduleDetailed(Schedule):
    hall: Hall | None = None
    film: Film | None = None
