from typing import Annotated, List

from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from sqlalchemy import update, select, delete

from src.crud.models import HallsRecord
from src.crud.queries.films import select_hall, select_halls
from src.crud.queries.utils import add_object, execute_safely
from src.schema.films import Hall
from src.schema.factories.film_factories import FilmFactory
from src.schema.users import User
from src.security.security import get_current_active_user

router = APIRouter(prefix="/halls", tags=["Halls"])


@router.get("/hall", status_code=200, tags=["Unfinished"])
async def get_halls(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:halls"])
        ],
        hall_name: str
) -> Hall:
    record = await select_hall(hall_name)

    if record is None:
        raise HTTPException(404, "Hall not found")

    return FilmFactory.get_hall(record)


@router.post("/hall", status_code=201, tags=["Unfinished"])
async def create_hall(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:halls"])
        ],
        hall: Hall
) -> Hall:
    await add_object(
        HallsRecord(
            hall_name=hall.hall_name,
            seats_per_row=hall.seats_per_row,
            no_of_rows=hall.no_of_rows
        )
    )

    record = await select_hall(hall.hall_name)
    return FilmFactory.get_hall(record)


@router.patch("/hall", status_code=201, tags=["Unfinished"])
async def update_hall(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:halls"])
        ],
        updated_hall: Hall
):
    query = update(
        HallsRecord
    ).values(
        hall_name=updated_hall.hall_name,
        seats_per_row=updated_hall.seats_per_row,
        no_of_rows=updated_hall.no_of_rows
    ).where(
        HallsRecord.hall_id == updated_hall.id
    )
    await execute_safely(query)

    record = await select_hall(updated_hall.hall_name)

    if not record:
        raise HTTPException(
          422, "Hall not found"
        )

    return FilmFactory.get_hall(record)


@router.get("/halls", status_code=200, tags=["Unfinished"])
async def get_halls(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:halls"])
        ],
        start: Annotated[int, Param(title="Start id", ge=1,)],
        limit: Annotated[int, Param(title="limit id to update", ge=2)]

) -> List[Hall]:
    records = await select_halls(start, limit)
    return FilmFactory.get_halls(records)


@router.delete("/hall", status_code=204, tags=["Unfinished"])
async def delete_hall(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:halls"])
        ],
        hall_name: str
):
    query = delete(
        HallsRecord
    ).where(
        HallsRecord.hall_name == hall_name
    )
    await execute_safely(query)


@router.get("/halls/schedules", tags=["Unfinished"])
async def get_schedules(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:halls"])
        ],
        hall_name: str
):
    # todo finish
    pass
