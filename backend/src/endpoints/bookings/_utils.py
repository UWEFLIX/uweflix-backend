from fastapi import HTTPException
from src.utils.utils import ALPHABETS
from src.crud.models import HallsRecord


_ALPH_TO_INT = {key: value for value, key in enumerate(ALPHABETS)}


def validate_seat(seat: str, hall: HallsRecord):
    row = 0
    index = 0

    for _index, alph in enumerate(seat):
        if alph.isalpha():
            try:
                letter_int = _ALPH_TO_INT[alph] + 1
            except KeyError:
                raise HTTPException(422, detail="Invalid seat")

            row += letter_int
            _index += 1
        else:
            break

    try:
        column = int(seat[index:])
    except ValueError:
        raise HTTPException(422, detail="Invalid seat")

    if row == 0 or column <= 0:
        raise HTTPException(422, detail="Invalid seat")

    if (row > hall.no_of_rows or
            column > hall.seats_per_row):
        raise HTTPException(status_code=422, detail="Seat out of range")

    return row, column
