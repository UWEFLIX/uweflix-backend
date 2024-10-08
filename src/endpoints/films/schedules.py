import asyncio
import datetime
from collections import defaultdict
from datetime import timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from icecream import ic
from sqlalchemy import delete, update, select, func, and_
from src.crud.models import SchedulesRecord, HallsRecord, FilmsRecord, SeatLocksRecord, BookingsRecord, AccountsRecord, \
    PersonTypesRecord
from src.crud.queries.films import (
    select_inserted_schedules, select_schedule, select_schedules,
    select_all_schedules, select_film_by_id
)
from src.crud.queries.utils import add_object, execute_safely, scalar_selection, all_selection
from src.schema.bookings import SeatNoStr, SeatLock, BatchBookings
from src.schema.factories.bookings_factory import BookingsFactory
from src.schema.factories.film_factories import FilmFactory
from src.schema.films import Schedule, Film
from src.schema.users import User
from src.security.security import get_current_active_user

router = APIRouter(prefix="/schedules", tags=["Schedules"])

_tzinfo = timezone(timedelta(hours=5, minutes=30))


def _get_timings(schedule: Schedule, duration: int):
    start = datetime.datetime(
        tzinfo=_tzinfo,
        year=schedule.show_time.year,
        month=schedule.show_time.month,
        day=schedule.show_time.day,
        minute=schedule.show_time.minute,
        second=schedule.show_time.second,
        hour=schedule.show_time.hour
    )
    end = start + timedelta(seconds=duration, minutes=15)

    return start, end


async def _check_time_conflicts(new_schedule: Schedule):
    """
    Check for time conflicts in schedules
    Args:
        new_schedule: the new schedule

    Returns: true none, raises 422 if conflict
    """
    records = await select_all_schedules()
    schedules = FilmFactory.get_detailed_schedules(records)

    _film_record = await select_film_by_id(new_schedule.film_id)
    _film = FilmFactory.get_half_film(_film_record["film"])
    this_start, this_end = _get_timings(new_schedule, _film.duration_sec)

    for schedule in schedules:
        that_start, that_end = _get_timings(schedule, schedule.film.duration_sec)
        if (
                that_start <= this_start <= that_end
        ) or (
                that_start <= this_end <= that_end
        ):
            raise HTTPException(
                422,
                f"Time Conflict with schedule ID {schedule.id}"
            )


@router.post("/schedule", status_code=201, tags=["Unfinished"])
async def create_schedule(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:schedules"])
        ],
        schedule: Schedule
):
    film_record: FilmsRecord = await select_film_by_id(schedule.film_id)

    if not film_record:
        raise HTTPException(
            404, "Film not found"
        )

    _film: Film = FilmFactory.get_half_film(film_record["film"])
    # Ensure all datetimes are timezone-aware (e.g., UTC)
    on_air_from = _film.on_air_from.astimezone(tz=timezone.utc)
    on_air_to = _film.on_air_to.astimezone(tz=timezone.utc)
    show_time = schedule.show_time.astimezone(tz=timezone.utc)

    # Now you can safely compare the datetime objects
    if not on_air_from <= show_time <= on_air_to:
        raise HTTPException(
            422,
            "Film is not active or not on air during this period"
        )

    record = SchedulesRecord(
        hall_id=schedule.hall_id,
        film_id=schedule.film_id,
        show_time=schedule.show_time,
        on_schedule=schedule.on_schedule,
        ticket_price=schedule.ticket_price,
    )

    _check = await _check_time_conflicts(schedule)

    await add_object(record)

    showtime = schedule.show_time.strftime("%Y-%m-%d %H:%M:%S")

    records = await select_inserted_schedules(
        record.film_id, record.hall_id, showtime
    )
    return FilmFactory.get_detailed_schedule(records)


@router.patch("/schedule", status_code=201, tags=["Unfinished"])
async def update_schedule(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:schedules"])
        ],
        updated: Schedule
):
    records = await select_schedule(updated.id)

    if records is None:
        raise HTTPException(
            404, "Schedule not found"
        )

    schedule = FilmFactory.get_detailed_schedule(records)

    query = update(
        SchedulesRecord
    ).values(
        on_schedule=updated.on_schedule,
        ticket_price=updated.ticket_price,
    ).where(
        SchedulesRecord.schedule_id == schedule.id
    )

    await execute_safely(query)

    showtime = schedule.show_time.strftime("%Y-%m-%d %H:%M:%S")

    records = await select_inserted_schedules(
        schedule.film_id, schedule.hall_id, showtime
    )
    return FilmFactory.get_detailed_schedule(records)


@router.get("/schedule/{schedule_id}", tags=["Unfinished"])
async def get_schedule(
        schedule_id: int
):
    records = await select_schedule(schedule_id)
    return FilmFactory.get_detailed_schedule(records)


@router.get("/schedules", tags=["Unfinished"])
async def get_schedules(
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)]
):
    records = await select_schedules(start, limit)
    return FilmFactory.get_detailed_schedules(records)


@router.post(
    "/seat-lock/{seat}/{user_id}/{schedule_id}/",
    status_code=201
)
async def seat_lock(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        seat: SeatNoStr, user_id: int, schedule_id: int
):
    query = select(
        SeatLocksRecord
    ).where(
        and_(
            SeatLocksRecord.seat == seat,
            SeatLocksRecord.schedule_id == schedule_id,
            SeatLocksRecord.is_manually_closed == False,
            SeatLocksRecord.created_at >= func.now() -
            timedelta(minutes=5)
        )
    )

    record = await scalar_selection(query)
    if not record:
        pass
    else:
        raise HTTPException(
            409,
            "Seat already locked by another user"
        )

    new_record = SeatLocksRecord(
        seat=seat,
        schedule_id=schedule_id,
        user_id=user_id
    )
    await add_object(new_record)
    return SeatLock(
        id=new_record.id,
        seat=new_record.seat,
        schedule_id=new_record.schedule_id,
        is_manually_closed=new_record.is_manually_closed,
        created_at=new_record.created_at,
        user_id=new_record.user_id,
    )


@router.patch(
    "/seat-lock-release/{seat_lock_id}/",
    status_code=201
)
async def seat_lock_release(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        seat_lock_id: int
):
    query = update(
        SeatLocksRecord
    ).values(
        is_manually_closed=1
    ).where(
        SeatLocksRecord.id == seat_lock_id
    )
    asyncio.create_task(execute_safely(query))


@router.get("/booking/{schedule_id}/", tags=["Schedules", "Bookings"])
async def bookings_per_schedule(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        schedule_id: int
):
    query = select(
        BookingsRecord, SchedulesRecord, FilmsRecord, HallsRecord,
        AccountsRecord, PersonTypesRecord
    ).join(
        SchedulesRecord,
        SchedulesRecord.schedule_id == BookingsRecord.schedule_id
    ).join(
        FilmsRecord,
        SchedulesRecord.film_id == FilmsRecord.film_id
    ).join(
        HallsRecord,
        HallsRecord.hall_id == SchedulesRecord.hall_id
    ).outerjoin(
        AccountsRecord, AccountsRecord.id == BookingsRecord.account_id
    ).join(
        PersonTypesRecord,
        PersonTypesRecord.person_type_id == BookingsRecord.person_type_id
    ).where(
        BookingsRecord.schedule_id == schedule_id
    )
    records = await all_selection(query)

    if not records:
        raise HTTPException(404, "No bookings found")
    return BookingsFactory.get_bookings(records)


@router.get("/scheduled/bookings/{schedule_id}", tags=["Bookings"])
async def get_bookings(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        schedule_id: int
):
    query = select(
        BookingsRecord, SchedulesRecord, FilmsRecord, HallsRecord,
        AccountsRecord, PersonTypesRecord
    ).join(
        SchedulesRecord,
        SchedulesRecord.schedule_id == BookingsRecord.schedule_id
    ).join(
        FilmsRecord,
        SchedulesRecord.film_id == FilmsRecord.film_id
    ).join(
        HallsRecord,
        HallsRecord.hall_id == SchedulesRecord.hall_id
    ).outerjoin(
        AccountsRecord, AccountsRecord.id == BookingsRecord.account_id
    ).join(
        PersonTypesRecord,
        PersonTypesRecord.person_type_id == BookingsRecord.person_type_id
    ).where(
        BookingsRecord.schedule_id == schedule_id
    )

    records = await all_selection(query)
    if records is None:
        return []

    bookings = BookingsFactory.get_bookings(records)

    data = defaultdict(BatchBookings)
    for booking in bookings:
        batch = data[booking.batch_ref]
        batch.batch_ref = booking.batch_ref
        batch.bookings.append(booking)

    return [v for k, v in data.items()]
