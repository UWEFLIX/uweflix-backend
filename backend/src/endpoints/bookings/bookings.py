import string
from collections import Counter
from random import choice
from typing import Annotated, List, Dict

from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param

from src.crud.models import BookingsRecord, PersonTypesRecord, SchedulesRecord, FilmsRecord
from src.crud.queries.bookings import (
    select_booking, select_club_bookings, select_user_bookings, get_details, select_batch, select_batches
)
from src.crud.queries.clubs import select_leader_clubs
from src.crud.queries.utils import add_object, add_objects
from src.endpoints.bookings.person_types import router as persons
from src.schema.bookings import SingleBooking, MultipleBookings, Booking
from src.schema.factories.bookings_factory import BookingsFactory
from src.schema.users import User
from src.security.security import get_current_active_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])
router.include_router(persons)


def generate_random_string(length=6) -> str:
    letters = string.ascii_uppercase
    return ''.join(choice(letters) for _ in range(length))


@router.get("/paid/booking", tags=["Unfinished"])
async def get_booking(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        booking_id: int
) -> Booking:
    records = await select_booking(booking_id)
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


@router.get("/club/bookings", tags=["Unfinished", "Clubs"])
async def get_club_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)],
        club_id: Annotated[int, Param(title="Club ID", ge=1)],
) -> List[Booking]:
    clubs = await select_leader_clubs(current_user.id)
    try:
        clubs[club_id]
    except KeyError:
        raise HTTPException(
            422, "You are not the leader of the club"
        )

    records = await select_club_bookings(start, limit, club_id)

    return BookingsFactory.get_bookings(records)


@router.get("/user/bookings", tags=["Unfinished", "Users"])
async def get_user_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)],
) -> List[Booking]:
    records = await select_user_bookings(start, limit, current_user.id)

    return BookingsFactory.get_bookings(records)


@router.post("/user/bookings", tags=["Unfinished", "Users"])
async def create_user_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        booking_request: SingleBooking
) -> List[Booking]:

    details = await get_details(
        current_user.id, "USER", booking_request.schedule.id
    )

    _persons = details["persons"]
    batches = details["batches"]
    accounts = details["accounts"]
    account = accounts.values()[0]

    try:
        person_record: PersonTypesRecord = _persons[booking_request.person_type.id]
    except KeyError:
        raise HTTPException(
            404, "Person type not found"
        )

    try:
        schedule_record: SchedulesRecord = details["schedule"]
    except KeyError:
        raise HTTPException(
            404, "Schedule not found"
        )

    while True:
        batch_reference = generate_random_string()
        if batch_reference not in batches:
            break

    amount = schedule_record.ticket_price * ((100 - person_record.discount_amount) / 100)

    record = BookingsRecord(
        seat_no=booking_request.seat_no,
        schedule_id=booking_request.schedule.id,
        person_type_id=booking_request.person_type.id,
        batch_ref=batch_reference,
        amount=amount,
        account_id=account.id,
    )
    await add_object(record)

    records = await select_batch(batch_reference)

    return BookingsFactory.get_bookings(records)


@router.post("/club/bookings", tags=["Unfinished", "Clubs"])
async def create_club_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        requests: MultipleBookings
) -> List[Booking]:
    clubs = await select_leader_clubs(current_user.id)
    try:
        clubs[requests.club_id]
    except KeyError:
        raise HTTPException(
            422, "You are not the leader of the club"
        )

    details = await get_details(
        current_user.id, "CLUB", requests.schedule_id
    )

    _persons = details["persons"]
    accounts = details["accounts"]
    batches = details["batches"]

    try:
        account = accounts[requests.account_id]
    except KeyError:
        raise HTTPException(404, "Account not found")

    try:
        schedule_record: SchedulesRecord = details["schedule"]
    except KeyError:
        raise HTTPException(
            404, "Schedule not found"
        )

    if account.status != "ENABLED":
        raise HTTPException(422, "Account is not enabled")

    while True:
        batch_reference = generate_random_string()
        if batch_reference not in batches:
            break

    final_booking_records = []
    for request in requests.bookings:
        try:
            person_record: PersonTypesRecord = _persons[request.person_type.id]
        except KeyError:
            raise HTTPException(
                404,
                f"Person type ID {request.person_type.id} not found"
            )

        # todo find if discounts stack like this
        discount = person_record.discount_amount + account.discount_rate

        if discount > 100:
            discount = 100

        amount = schedule_record.ticket_price * (
                (100 - discount) / 100
        )

        record = BookingsRecord(
            seat_no=request.seat_no,
            schedule_id=request.schedule.id,
            person_type_id=request.person_type.id,
            batch_ref=batch_reference,
            amount=amount,
            account_id=account.id,
        )
        final_booking_records.append(record)
        batches[batch_reference] = batch_reference

    await add_objects(final_booking_records)

    records = select_batch(batch_reference)
    return BookingsFactory.get_bookings(records)


@router.get("/batch/bookings", tags=["Unfinished"])
async def get_batch_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:bookings"])
        ],
        batch_reference: str
) -> List[Booking]:
    records = select_batch(batch_reference)
    return BookingsFactory.get_bookings(records)


@router.get("/batches", tags=["Unfinished"])
async def get_batch_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:bookings"])
        ],
) -> Dict[str, int]:
    """returns counts of batches"""
    records: List[BookingsRecord] = await select_batches()
    references = Counter(x.batch_ref for x in records)
    return references

