from typing import Annotated, List

from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from sqlalchemy import update, select, delete

from src.crud.models import CardsRecord, CitiesRecord
from src.crud.queries.accounts import select_card
from src.crud.queries.clubs import select_city, select_cities
from src.crud.queries.utils import add_object, execute_safely
from src.schema.clubs import City
from src.schema.factories.account_factory import AccountsFactory
from src.schema.factories.club_factories import ClubFactory
from src.schema.users import User
from src.security.security import get_current_active_user

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("/city", status_code=200, tags=["Unfinished"])
async def get_cities(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:cities"])
        ],
        city_name: str
) -> City:
    record = await select_city(city_name)

    if record is None:
        raise HTTPException(404, "City not found")

    return ClubFactory.get_city(record)


@router.post("/city", status_code=201, tags=["Unfinished"])
async def create_city(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:cities"])
        ],
        city_name: str
) -> City:
    await add_object(
        CitiesRecord(
            city_name=city_name
        )
    )

    record = await select_city(city_name)
    return ClubFactory.get_city(record)


@router.patch("/city", status_code=201, tags=["Unfinished"])
async def update_city(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:cities"])
        ],
        updated_city: City
):
    query = update(
        CitiesRecord
    ).values(
        city_name=updated_city.name
    ).where(
        CitiesRecord.city_id == updated_city.id
    )
    await execute_safely(query)

    record = await select_city(updated_city.name)
    return ClubFactory.get_city(record)


@router.get("/cities", status_code=200, tags=["Unfinished"])
async def get_cities(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:cities"])
        ],
        start: Annotated[int, Param(title="Start id", ge=1,)],
        limit: Annotated[int, Param(title="limit id to update", ge=2)]

) -> List[City]:
    records = await select_cities(start, limit)
    return ClubFactory.get_cities(records)


@router.delete("/city", status_code=204, tags=["Unfinished"])
async def delete_city(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:halls"])
        ],
        city_name: str
):
    query = delete(
        CitiesRecord
    ).where(
        CitiesRecord.city_name == city_name
    )
    await execute_safely(query)
