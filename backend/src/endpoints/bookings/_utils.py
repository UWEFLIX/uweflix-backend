from fastapi import HTTPException
from src.utils.utils import ALPHABETS
from src.crud.models import HallsRecord


_ALPH_TO_INT = {key: value for value, key in enumerate(ALPHABETS)}


def validate_seat(seat: str, hall: HallsRecord):
    if len(seat) != 2:
        raise HTTPException(status_code=422, detail="Invalid seat")

    submitted_row_str = seat[0]

    try:
        submitted_column = int(seat[1])
        submitted_row = _ALPH_TO_INT[submitted_row_str]
    except (ValueError, KeyError):
        raise HTTPException(status_code=422, detail="Invalid seat")

    if submitted_row > hall.no_of_rows or submitted_column > hall.seats_per_row:
        raise HTTPException(status_code=422, detail="Seat out of range")
