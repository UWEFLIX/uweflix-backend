from typing import Annotated, List

from fastapi import APIRouter, Security, HTTPException, UploadFile, File
from fastapi.params import Param
from sqlalchemy import delete, update

from src.crud.models import FilmsRecord
from src.crud.queries.films import select_film, select_films
from src.crud.queries.utils import add_object, execute_safely
from src.endpoints.films.halls import router as halls
from src.schema.factories.film_factories import FilmFactory
from src.schema.films import Film
from src.schema.users import User
from src.security.security import get_current_active_user
from src.endpoints.films.halls import router as images
from src.endpoints.films.schedules import router as schedules

router = APIRouter(prefix="/films", tags=["Films"])
router.include_router(halls)
router.include_router(images)
router.include_router(schedules)


@router.post("/film", status_code=201, tags=["Unfinished"])
async def create_film(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        film: Film
) -> Film:

    if not film.poster_image:
        raise HTTPException(
            422, "Expecting poster_image to be a byte"
        )

    record = FilmsRecord(
        film_id=film.id,
        title=film.title,
        age_rating=film.age_rating,
        duration_sec=film.duration_sec,
        trailer_desc=film.trailer_desc,
        on_air_from=film.on_air_from,
        on_air_to=film.on_air_to,
        is_active=film.is_active,
        poster_image=f"{film.title}-poster.jpg",
    )

    await add_object(record)

    # todo save poster image to file

    records = await select_film(film.title)
    return FilmFactory.get_full_film(records)


@router.delete("/film", status_code=204, tags=["Unfinished"])
async def delete_film(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        title: str
):
    query = delete(
        FilmsRecord
    ).where(
        FilmsRecord.title == title
    )
    await execute_safely(query)


@router.patch("/film", status_code=204, tags=["Unfinished"])
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
        FilmsRecord.film_id==film.id
    )
    await execute_safely(query)

    records = await select_film(film.title)
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
            422, detail="Film not found"
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
