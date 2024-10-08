import datetime
from sqlalchemy import update
from typing import Annotated, List
from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from pydantic import EmailStr
from src.crud.models import (
    SchedulesRecord, PersonTypesRecord, BookingsRecord, AccountsRecord
)
from src.crud.queries.bookings import (
    select_club_bookings, get_details, select_batch, select_booking
)
from src.crud.queries.clubs import select_leader_clubs
from src.crud.queries.utils import add_objects, execute_safely
from src.endpoints.bookings._utils import validate_seat_per_hall
from src.schema.bookings import Booking, MultipleBookings
from src.schema.factories.bookings_factory import BookingsFactory
from src.schema.users import User
from src.security.security import get_current_active_user
from src.utils.utils import generate_random_string

router = APIRouter(prefix="/club", tags=["Clubs"])


@router.get("/bookings", tags=["Unfinished", "Clubs"])
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


@router.post("/booking", status_code=201, tags=["Unfinished", "Clubs"])
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
            422, "You are not the leader of the club or "
                 "club doesnt exist"
        )

    details = await get_details(
        requests.club_id, "CLUB", requests.schedule_id
    )

    _persons = details["persons"]
    accounts = details["accounts"]
    batches = details["batches"]
    members = details["club_members"]
    hall = details["halls"]

    try:
        account = accounts[requests.account_id]
    except KeyError:
        raise HTTPException(404, "Account not found")

    try:
        schedule_record: SchedulesRecord = details["schedules"]
    except KeyError:
        raise HTTPException(
            404, "Schedule not found"
        )

    if not schedule_record.on_schedule:
        raise HTTPException(
            422, "Schedule is not on schedule"
        )

    if schedule_record.show_time < datetime.datetime.now():
        raise HTTPException(
            422, "Cannot book for a past schedule"
        )

    if account.status != "ENABLED":
        raise HTTPException(403, "Account is not enabled")

    while True:
        batch_reference = generate_random_string()
        if batch_reference not in batches:
            break

    final_booking_records = []
    total = 0
    for request in requests.bookings:
        try:
            person_record: PersonTypesRecord = _persons[request.person_type_id]
        except KeyError:
            raise HTTPException(
                404,
                f"Person type ID {request.person_type_id} not found"
            )

        validate_seat_per_hall(request.seat_no, hall)

        try:
            members[request.user_id]
        except KeyError as e:
            raise HTTPException(
                422,
                f"user id {request.user_id} doesnt exist or is not in your club"
            )

        # todo find if discounts stack like this
        discount = person_record.discount_amount + account.discount_rate

        if discount > 100:
            discount = 100

        amount = schedule_record.ticket_price * (
                (100 - discount) / 100
        )
        total += amount

        record = BookingsRecord(
            seat_no=request.seat_no,
            schedule_id=requests.schedule_id,
            person_type_id=request.person_type_id,
            batch_ref=batch_reference,
            amount=amount,
            account_id=account.id,
            assigned_user=request.user_id
        )
        final_booking_records.append(record)

    if account.balance - total < 0:
        raise HTTPException(404, "Money not found")

    await add_objects(final_booking_records)

    query = update(
        AccountsRecord
    ).values(
        balance=AccountsRecord.balance - total
    ).where(AccountsRecord.id == account.id)
    await execute_safely(query)

    records = await select_batch(batch_reference)
    return BookingsFactory.get_bookings(records)


@router.patch("/booking", status_code=201, tags=["Unfinished", "Users"])
async def reassign_user_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        booking_id: int,
        new_assignee: EmailStr
) -> Booking:

    records = await select_booking(booking_id)

    if not records:
        raise HTTPException(404, "")

    booking = BookingsFactory.get_booking(records)
    if booking.account.entity_type != "USER" and booking.account.entity_id:
        raise HTTPException(
            403,
            "You do not have rights to edit this booking"
        )

    clubs = await select_leader_clubs(current_user.id)
    try:
        clubs[booking.account.entity_id]
    except KeyError:
        raise HTTPException(
            422, "You are not the leader of the club"
        )

    details = await get_details(
        current_user.id, "CLUB", booking.schedule.id
    )

    members = details["members"]
    try:
        members[new_assignee]
    except KeyError:
        raise HTTPException(
            422,
            f"{new_assignee} doesnt exist or is not in your club"
        )

    query = update(
        BookingsRecord
    ).values(
        assigned_user=new_assignee
    ).where(
        BookingsRecord.id == booking_id
    )

    await execute_safely(query)

    records = await select_booking(booking_id)
    return BookingsFactory.get_booking(records)
