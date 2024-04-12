from typing import Annotated

from fastapi import APIRouter, Security, UploadFile, File, HTTPException

from src.crud.models import SchedulesRecord
from src.crud.queries.utils import add_object
from src.schema.films import Schedule
from src.schema.users import User
from src.security.security import get_current_active_user


router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post("/schedule", status_code=201, tags=["Unfinished"])
async def create_schedule(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:schedules"])
        ],
        schedule: Schedule
):

    if not schedule.film:
        raise HTTPException(
            422, "The schedule film should not be null"
        )
    if not schedule.hall:
        raise HTTPException(
            422, "The schedule hall should not be null"
        )

    record = SchedulesRecord(
        schedule_id=schedule.id,
        hall_id=schedule.hall.id,
        film_id=schedule.film.id,
        show_time=schedule.show_time,
        on_schedule=schedule.on_schedule,
        ticket_price=schedule.ticket_price,
    )
    await add_object(record)


