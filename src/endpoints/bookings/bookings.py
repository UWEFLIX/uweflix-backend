import asyncio
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Annotated, Dict, List

from fastapi import APIRouter, Security, HTTPException, Path
from sqlalchemy import select, update, text, and_, func, delete

from src.crud.models import (
    BookingsRecord, AccountsRecord, PersonTypesRecord, SchedulesRecord, HallsRecord, SeatLocksRecord, FilmsRecord
)
from src.crud.queries.accounts import select_account
from src.crud.queries.bookings import (
    select_booking, select_batches, select_batch
)
from src.crud.queries.clubs import select_leader_clubs
from src.crud.queries.utils import scalars_selection, scalar_selection, add_object, execute_safely, all_selection
from src.endpoints.bookings._utils import validate_seat_per_hall
from src.endpoints.bookings.clubs import router as clubs_router
from src.endpoints.bookings.person_types import router as persons
from src.endpoints.bookings.users import router as users_router
from src.schema.bookings import Booking, BatchData, SingleBooking, Reporting, SeatNoStr, SeatLock, FilmSalesReport
from src.schema.factories.bookings_factory import BookingsFactory
from src.schema.users import User
from src.security.security import get_current_active_user

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
            User, Security(get_current_active_user, scopes=[])
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
            User, Security(get_current_active_user, scopes=[])
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


@router.get("/bookings/batch-ref/{batch_ref}", tags=["Unfinished"])
async def get_batch(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        batch_ref: str
):
    query = select(
        BookingsRecord
    ).where(
        BookingsRecord.batch_ref == batch_ref
    )
    records = await scalars_selection(query)

    return BookingsFactory.get_half_bookings(records)


@router.get("/account/bookings/{account_id}")
async def get_account_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:reports"])
        ],
        account_id: int,
):
    query = select(
        BookingsRecord
    ).where(
        BookingsRecord.account_id == account_id
    )
    records: List[BookingsRecord] = await scalars_selection(query)
    monthly_data = defaultdict(Reporting)

    for record in records:
        timeframe = record.created.strftime("%m-%Y")
        report = monthly_data[timeframe]
        report.amount += record.amount
        report.count += 1

    return monthly_data


@router.post("/admin/booking/{cash}/")
async def create_admin_side_booking(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:bookings"])
        ],
        booking_request: SingleBooking,
        cash: Annotated[int, Path(title="Is the customer paying by cash", ge=0, le=1)]
):
    accounts_query = select(
        AccountsRecord
    ).where(
        AccountsRecord.id == booking_request.account_id
    )
    person_type_query = select(
        PersonTypesRecord
    ).where(
        PersonTypesRecord.person_type_id == booking_request.person.person_type_id
    )
    schedule_query = select(
        SchedulesRecord
    ).where(
        SchedulesRecord.schedule_id == booking_request.schedule_id
    )

    account_record, person_type_record, schedule_record = await asyncio.gather(
        select_account(accounts_query), scalar_selection(person_type_query),
        scalar_selection(schedule_query)
    )

    if account_record is None:
        raise HTTPException(404, "Account not found")

    if person_type_record is None:
        raise HTTPException(404, "Person type not found")

    if account_record.status != "ENABLED":
        raise HTTPException(403, "Account is not enabled")

    if schedule_record is None:
        raise HTTPException(
            404, "Schedule not found"
        )

    hall_query = select(
        HallsRecord
    ).where(
        HallsRecord.hall_id == schedule_record.hall_id
    )

    hall_record = await scalar_selection(hall_query)

    validate_seat_per_hall(booking_request.person.seat_no, hall_record)

    if schedule_record.show_time < datetime.now():
        raise HTTPException(
            422, "Cannot book for a past schedule"
        )

    amount = schedule_record.ticket_price * (
            (100 - person_type_record.discount_amount) / 100
    )
    if not cash:
        if account_record.balance - amount < 0:
            raise HTTPException(404, "Money not found")

    record = BookingsRecord(
        seat_no=booking_request.person.seat_no,
        schedule_id=booking_request.schedule_id,
        person_type_id=booking_request.person.person_type_id,
        batch_ref=text("generate_unique_string()"),
        amount=amount,
        assigned_user=booking_request.person.user_id,
        account_id=account_record.id,
    )
    await add_object(record)
    query = select(BookingsRecord).where(BookingsRecord.id == record.id)
    booking = await scalar_selection(query)

    records = await select_batch(booking.batch_ref)

    if not cash:
        query = update(
            AccountsRecord
        ).values(
            balance=AccountsRecord.balance - amount
        ).where(AccountsRecord.id == account_record.id)
        asyncio.create_task(execute_safely(query))

    return BookingsFactory.get_bookings(records)[0]


@router.get("/film/bookings-count/")
async def get_sales_count(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:reports"])
        ],
        # count: int
) -> dict[int, FilmSalesReport]:
    query = select(
        BookingsRecord, FilmsRecord
    ).join(
        SchedulesRecord, BookingsRecord.schedule_id == SchedulesRecord.schedule_id
    ).join(
        FilmsRecord, FilmsRecord.film_id == SchedulesRecord.film_id
    )

    records = await all_selection(query)
    data = defaultdict(FilmSalesReport)

    for record in records:
        report = data[record[1].film_id]
        report.film_title = record[1].title
        report.bookings += 1

    return data
