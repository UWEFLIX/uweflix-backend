from typing import Annotated

from fastapi import APIRouter, Security

from src.crud.queries.bookings import select_booking
from src.endpoints.bookings.person_types import router as persons
from src.schema.factories.bookings_factory import BookingsFactory
from src.schema.users import User
from src.security.security import get_current_active_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])
router.include_router(persons)


@router.get("/booking", tags=["Unfinished"])
async def get_booking(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        booking_id: int
):
    # todo security
    records = await select_booking(booking_id)
    return BookingsFactory.get_booking(records)
