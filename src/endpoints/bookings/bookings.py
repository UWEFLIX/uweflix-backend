from typing import Annotated, Dict, List
from fastapi import APIRouter, Security, HTTPException
from sqlalchemy import select

from src.crud.models import BookingsRecord
from src.crud.queries.bookings import (
    select_booking, select_batches, select_batch
)
from src.crud.queries.clubs import select_leader_clubs
from src.crud.queries.utils import scalars_selection
from src.endpoints.bookings.person_types import router as persons
from src.schema.bookings import Booking, BatchData
from src.schema.factories.bookings_factory import BookingsFactory
from src.schema.users import User
from src.security.security import get_current_active_user
from src.endpoints.bookings.users import router as users_router
from src.endpoints.bookings.clubs import router as clubs_router

router = APIRouter(prefix="/bookings", tags=["Bookings"])
router.include_router(persons)
router.include_router(users_router)
router.include_router(clubs_router)


@router.get("/paid/booking/{booking_id}", tags=["Unfinished"])
async def get_booking(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        booking_id: int
) -> Booking:
    records = await select_booking(booking_id)

    if not records:
        raise HTTPException(404, "")

    booking = BookingsFactory.get_booking(records)

    if "read:bookings" in current_user.permissions:
        return booking

    if booking.account.entity_type == "CLUB":
        clubs = await select_leader_clubs(current_user.id)
        try:
            clubs[booking.account.entity_id]
        except KeyError:
            raise HTTPException(
                422, "You are not the leader of the club"
            )
    else:
        if booking.account.entity_id != current_user.id:
            raise HTTPException(
                422, "Not your booking"
            )

    return booking


@router.get("/batches", tags=["Unfinished"])
async def get_batch_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:bookings"])
        ],
) -> Dict[str, BatchData]:
    """returns batch data"""
    return await select_batches()


@router.get("/batch/bookings/{batch_reference}", tags=["Unfinished"])
async def get_batch_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:bookings"])
        ],
        batch_reference: str
) -> List[Booking]:
    records = await select_batch(batch_reference)

    if not records:
        raise HTTPException(404, "No bookings found")

    return BookingsFactory.get_bookings(records)


@router.get("/bookings/booked-seats/{schedule_id}", tags=["Unfinished"])
async def get_batch_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:bookings"])
        ],
        schedule_id: int
) -> List[str]:
    query = select(
        BookingsRecord
    ).where(
        BookingsRecord.schedule_id == schedule_id
    )
    records = await scalars_selection(query)

    return [
        record.seat_no for record in records
    ]
