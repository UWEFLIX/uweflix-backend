from fastapi import HTTPException

from src.schema.bookings import SeatNoStr, SEAT_NO_DELIMITER
from src.utils.utils import ALPHABETS
from src.crud.models import HallsRecord


_ALPH_TO_INT = {key: value for value, key in enumerate(ALPHABETS)}


def titleToNumber(string: str) -> int:
    """
    Author: GeeksForGeeks
    https://www.geeksforgeeks.org/find-excel-column-number-column-title/
    This process is similar to binary-to-decimal conversion
    """
    result = 0
    for B in range(len(string)):
        result *= 26
        result += ord(string[B]) - ord('A') + 1

    return result


def validate_seat_per_hall(seat: SeatNoStr, hall: HallsRecord):
    split = seat.split(SEAT_NO_DELIMITER)

    row_alph = split[0]
    column = int(split[1])
    row = titleToNumber(row_alph)

    if row > hall.no_of_rows:
        raise HTTPException(
            422, "This hall doesnt have this row number"
        )
    if column > hall.seats_per_row:
        raise HTTPException(
            422, "This hall doesnt have this column number"
        )

    return row, column
