from typing import Annotated, List

from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from sqlalchemy import update, select

from src.crud.models import CardsRecord, CitiesRecord
from src.crud.queries.accounts import select_card
from src.crud.queries.clubs import select_city, select_cities
from src.crud.queries.utils import add_object, execute_safely
from src.schema.clubs import City
from src.schema.factories.account_factory import AccountsFactory
from src.schema.factories.club_factories import ClubFactory
from src.schema.users import User, Card
from src.security.security import get_current_active_user

router = APIRouter(prefix="/person-types", tags=["Persons"])


@router.get("/person-types", status_code=200, tags=["Unfinished"])
async def get_person(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:persons"])
        ],
        person_type: str
) -> City:
    record = await select_person_type(person_type)

    if record is None:
        raise HTTPException(404, "Person Type not found")

    return ClubFactory.get_city(record)


@router.post("/person-type", status_code=201, tags=["Unfinished"])
async def create_person(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:persons"])
        ],
        person_type: str
) -> City:
    await add_object(
        CitiesRecord(
            person_type=person_type
        )
    )

    record = await select_city(person_type)
    return ClubFactory.get_city(record)


@router.patch("/person-type", status_code=201, tags=["Unfinished"])
async def create_person_type(
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


@router.get("/person-types", status_code=200, tags=["Unfinished"])
async def get_person_types(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:cities"])
        ],
        start: Annotated[int, Param(title="Start id", ge=1,)],
        limit: Annotated[int, Param(title="limit id to update", ge=2)]

) -> List[City]:
    records = await select_cities(start, limit)
    return ClubFactory.get_cities(records)
