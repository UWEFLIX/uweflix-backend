import asyncio
from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param, Path
from pydantic import EmailStr
from sqlalchemy import update, select
from src.crud.models import (
    PersonTypesRecord, SchedulesRecord, BookingsRecord, AccountsRecord
)
from src.crud.queries.bookings import (
    select_user_bookings, get_details, select_batch, select_booking,
    select_assigned_bookings
)
from src.crud.queries.utils import (
    add_object, execute_safely, add_objects, scalar_selection
)
from src.endpoints.bookings._utils import validate_seat_per_hall
from src.schema.bookings import Booking, SingleBooking, MultipleBookings
from src.schema.factories.bookings_factory import BookingsFactory
from src.schema.users import User
from src.security.security import get_current_active_user
from src.utils.utils import generate_random_string

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/bookings", tags=["Unfinished", "Users"])
async def get_user_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)],
) -> List[Booking]:
    records = await select_user_bookings(start, limit, current_user.id)

    return BookingsFactory.get_bookings(records)


@router.post("/booking", status_code=201, tags=["Unfinished", "Users"])
async def create_user_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        booking_request: SingleBooking
) -> Booking:

    details = await get_details(
        current_user.id, "USER", booking_request.schedule_id
    )

    if details["schedules"] is None:
        raise HTTPException(404, "No schedule found")

    _persons = details["persons"]
    batches = details["batches"]
    accounts: dict = details["accounts"]
    hall = details["halls"]

    try:
        account = accounts[booking_request.account_id]
    except KeyError:
        raise HTTPException(
            404,
            "Account not found, or not available for you"
        )

    if account.status != "ENABLED":
        raise HTTPException(403, "Account is not enabled")

    try:
        schedule_record: SchedulesRecord = details["schedules"]
    except KeyError:
        raise HTTPException(
            404, "Schedule not found"
        )

    if not schedule_record.hall_id:
        raise HTTPException(404, "Schedule not found")

    if not schedule_record.on_schedule:
        raise HTTPException(
            422, "Schedule cancelled"
        )

    validate_seat_per_hall(booking_request.person.seat_no, hall)

    try:
        person_record: PersonTypesRecord = _persons[
            booking_request.person.person_type_id
        ]
    except KeyError:
        raise HTTPException(
            404, "Person type not found"
        )

    if schedule_record.show_time < datetime.now():
        raise HTTPException(
            422, "Cannot book for a past schedule"
        )

    while True:
        batch_reference = generate_random_string()
        if batch_reference not in batches:
            break

    amount = schedule_record.ticket_price * (
            (100 - person_record.discount_amount) / 100
    )

    if account.balance - amount < 0:
        raise HTTPException(404, "Money not found")

    record = BookingsRecord(
        seat_no=booking_request.person.seat_no,
        schedule_id=booking_request.schedule_id,
        person_type_id=booking_request.person.person_type_id,
        batch_ref=batch_reference,
        amount=amount,
        assigned_user=booking_request.person.user_id,
        account_id=account.id,
    )
    await add_object(record)

    query = update(
        AccountsRecord
    ).values(
        balance=AccountsRecord.balance - amount
    ).where(AccountsRecord.id == account.id)
    asyncio.create_task(execute_safely(query))

    records = await select_batch(batch_reference)

    return BookingsFactory.get_bookings(records)[0]


@router.patch("/booking", tags=["Unfinished", "Users"])
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


@router.get("/bookings/me", tags=["Unfinished", "Users"])
async def get_assigned_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
):
    records = await select_assigned_bookings(current_user.id)

    return BookingsFactory.get_bookings(records)


@router.post("/bookings/multiple/{cash}", status_code=201, tags=["Unfinished"])
async def create_club_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        requests: MultipleBookings,
        cash: Annotated[int, Path(title="If collected in cash or not", ge=0, le=1)],
) -> List[Booking]:
    schedule_record = select(
        SchedulesRecord
    ).where(
        SchedulesRecord.schedule_id == requests.schedule_id
    )
    account_query = select(
        AccountsRecord
    ).where(
        AccountsRecord.id == requests.account_id
    )
    schedule_record, account_record = await asyncio.gather(
        scalar_selection(schedule_record), scalar_selection(account_query)
    )

    if schedule_record is None:
        raise HTTPException(404, "Schedule not found")
    if account_record is None:
        raise HTTPException(404, "Account not found")

    price = schedule_record.ticket_price
    total = price * len(requests.bookings)

    if not cash and account_record.ballance - total < 0:
        raise HTTPException(404, "Money not found")

    booking_records = []
    batch_reference = generate_random_string()
    for booking in requests.bookings:
        record = BookingsRecord(
            seat_no=booking.seat_no,
            schedule_id=requests.schedule_id,
            account_id=requests.account_id,
            amount=schedule_record.ticket_price,
            person_type_id=booking.person_type_id,
            batch_ref=batch_reference,
            assigned_user=booking.user_id
        )
        booking_records.append(record)

    await add_objects(booking_records)

    if not cash:
        query = update(
            AccountsRecord
        ).values(
            balance=AccountsRecord.balance - total
        ).where(AccountsRecord.id == account_record.id)
        asyncio.create_task(execute_safely(query))

    records = await select_batch(batch_reference)
    return BookingsFactory.get_bookings(records)
