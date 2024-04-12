import datetime
from datetime import timedelta, tzinfo, timezone
from typing import Annotated

from fastapi import APIRouter, Security, UploadFile, File, HTTPException
from fastapi.params import Param
from sqlalchemy import delete, update, select
from src.crud.models import SchedulesRecord, HallsRecord, FilmsRecord
from src.crud.queries.films import select_inserted_schedules, select_schedule, select_schedules, select_all_schedules, \
    select_film_by_id
from src.crud.queries.utils import add_object, execute_safely
from src.schema.factories.film_factories import FilmFactory
from src.schema.films import Schedule, Film, ScheduleDetailed
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
    query = select(
        SchedulesRecord, FilmsRecord, HallsRecord
    )
    records = await select_all_schedules()
    schedules = FilmFactory.get_detailed_schedules(records)

    _film_record = await select_film_by_id(new_schedule.film_id)
    _film = FilmFactory.get_half_film(_film_record)
    startTimeB, endTimeB = _get_timings(new_schedule, _film.duration_sec)

    for schedule in schedules:
        startTimeA, endTimeA = _get_timings(new_schedule, _film.duration_sec)

        if (
                startTimeA <= startTimeB <= endTimeA
        ) or (
                startTimeA <= endTimeB <= endTimeA
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
        schedule: Schedule
):
    query = update(
        SchedulesRecord
    ).values(
        hall_id=schedule.hall_id,
        film_id=schedule.film_id,
        show_time=schedule.show_time,
        on_schedule=schedule.on_schedule,
        ticket_price=schedule.ticket_price,
    ).where(
        SchedulesRecord.schedule_id == schedule.id
    )

    _check = await _check_time_conflicts(schedule)

    await execute_safely(query)

    showtime = schedule.show_time.strftime("%Y-%m-%d %H:%M:%S")

    records = await select_inserted_schedules(
        schedule.film_id, schedule.hall_id, showtime
    )
    return FilmFactory.get_detailed_schedule(records)


@router.get("/schedule", tags=["Unfinished"])
async def get_schedule(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        schedule_id: int
):
    records = await select_schedule(schedule_id)
    return FilmFactory.get_detailed_schedule(records)


@router.get("/schedules", tags=["Unfinished"])
async def get_schedules(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)]
):
    records = await select_schedules(start, limit)
    return FilmFactory.get_detailed_schedules(records)


@router.delete("/schedule", tags=["Unfinished"], status_code=204)
async def delete_schedule(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:schedules"])
        ],
        schedule_id: int
):
    query = delete(
        SchedulesRecord
    ).where(
        SchedulesRecord.schedule_id == schedule_id
    )
    await execute_safely(query)
