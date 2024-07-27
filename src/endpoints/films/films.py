import os
from datetime import datetime
from typing import Annotated, List

import aiofiles
from fastapi import APIRouter, Security, HTTPException, File, UploadFile, Form, Body
from fastapi.params import Param
from sqlalchemy import update, select, and_, func, asc
from src.crud.models import FilmsRecord, SchedulesRecord, HallsRecord
from src.crud.queries.films import (
    select_film, select_films, select_film_schedules, select_film_by_id
)
from src.crud.queries.utils import add_object, execute_safely, all_selection
from src.endpoints.films.halls import router as halls
from src.schema.factories.film_factories import FilmFactory
from src.schema.films import Film, Schedule, ScheduleDetailed
from src.schema.users import User
from src.security.security import get_current_active_user
from src.endpoints.films.film_images import router as images, rename_poster
from src.endpoints.films.schedules import router as schedules
from src.utils.utils import str_to_iso_format

router = APIRouter(prefix="/films", tags=["Films"])
router.include_router(halls)
router.include_router(images)
router.include_router(schedules)


_ASSETS_DIR = os.getenv('ASSETS_FOLDER')
_FILMS_DIR = os.path.join(_ASSETS_DIR, 'images/films')


@router.post("/film", status_code=201, tags=["Unfinished"])
async def create_film(
        current_user: Annotated[
            User, Security(
                get_current_active_user, scopes=["write:films"]
            )
        ],
        film: Film = Body(...)
) -> Film:

    if type(film.on_air_to) is str:
        film.on_air_to = str_to_iso_format(film.on_air_to)

    if type(film.on_air_from) is str:
        film.on_air_from = str_to_iso_format(film.on_air_from)

    on_air_to = film.on_air_to.strftime(
        '%Y-%m-%d %H:%M:%S'
    )
    on_air_from = film.on_air_from.strftime(
        '%Y-%m-%d %H:%M:%S'
    )

    record = FilmsRecord(
        film_id=film.id,
        title=film.title,
        age_rating=film.age_rating,
        duration_sec=film.duration_sec,
        trailer_desc=film.trailer_desc,
        on_air_from=on_air_from,
        on_air_to=on_air_to,
        is_active=film.is_active,
    )

    await add_object(record)
    records = await select_film(film.title)

    return FilmFactory.get_full_film(records)


@router.patch("/film", status_code=201, tags=["Unfinished"])
async def update_film(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        film: Film
):
    query = update(
        FilmsRecord
    ).values(
        title=film.title,
        age_rating=film.age_rating,
        duration_sec=film.duration_sec,
        trailer_desc=film.trailer_desc,
        on_air_from=film.on_air_from,
        on_air_to=film.on_air_to,
        is_active=film.is_active,
    ).where(
        FilmsRecord.id == film.id
    )
    await execute_safely(query)

    records = await select_film(film.title)

    if not records:
        raise HTTPException(
            404, "Film not found"
        )

    return FilmFactory.get_full_film(records)


@router.get("/film/{film_id}", tags=["Unfinished"])
async def get_film_by_id(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        film_id: int
) -> Film:
    records = await select_film_by_id(film_id)

    if not records:
        raise HTTPException(
            404, detail="Film not found"
        )

    return FilmFactory.get_full_film(records)


@router.get("/film", tags=["Unfinished"])
async def get_film(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        title: str
) -> Film:
    records = await select_film(title)

    if not records:
        raise HTTPException(
            404, detail="Film not found"
        )

    return FilmFactory.get_full_film(records)


@router.get("/films", tags=["Unfinished"])
async def get_films(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)]
) -> List[Film]:
    records = await select_films(start, limit)

    return FilmFactory.get_half_films(records)


@router.get("/film/schedules", tags=["Unfinished"])
async def get_schedules(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        title: str
):
    query = select(
        FilmsRecord, SchedulesRecord
    ).outerjoin(
        SchedulesRecord,
        FilmsRecord.film_id == SchedulesRecord.film_id
    ).where(
        FilmsRecord.title == title
    )

    records = await select_film_schedules(query)

    if records is None:
        raise HTTPException(
            404, "Film not found"
        )

    return FilmFactory.get_film_schedules(records)


@router.get("/film/schedules/id/{film_id}", tags=["Unfinished"])
async def get_schedules_by_film_id(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        film_id: int
) -> List[ScheduleDetailed]:
    query = select(
        FilmsRecord, SchedulesRecord, HallsRecord
    ).outerjoin(
        SchedulesRecord,
        FilmsRecord.film_id == SchedulesRecord.film_id
    ).join(
        HallsRecord,
        HallsRecord.hall_id == SchedulesRecord.hall_id
    ).where(
        and_(
            FilmsRecord.film_id == film_id,
            SchedulesRecord.show_time > func.now()
        )
    ).order_by(asc(SchedulesRecord.show_time))

    records = await all_selection(query)

    if records is None:
        raise HTTPException(
            404, "Film not found"
        )

    _schedules = []
    for record in records:
        if not record:
            continue

        _schedules.append(
            ScheduleDetailed(
                **FilmFactory.get_schedule(
                    record[1]
                ).model_dump(),
                hall=FilmFactory.get_hall(record[2])
            )
        )

    return _schedules
