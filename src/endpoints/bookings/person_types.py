from typing import Annotated, List
from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from sqlalchemy import update, delete
from src.crud.models import PersonTypesRecord
from src.crud.queries.bookings import select_person_type, select_person_types
from src.crud.queries.utils import add_object, execute_safely
from src.schema.bookings import PersonType
from src.schema.factories.bookings_factory import BookingsFactory
from src.schema.users import User
from src.security.security import get_current_active_user

router = APIRouter(prefix="/person-types", tags=["Persons"])


@router.get("/person-type", status_code=200, tags=["Unfinished"])
async def get_person(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:person-types"])
        ],
        person_type: str
) -> PersonType:
    record = await select_person_type(person_type)

    if record is None:
        raise HTTPException(404, "Person Type not found")

    return BookingsFactory.get_person_type(record)


@router.get("/person-types", status_code=200, tags=["Unfinished"])
async def get_person_types(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:person-types"])
        ],
        start: Annotated[int, Param(title="Start id", ge=1,)],
        limit: Annotated[int, Param(title="limit id to update", ge=2)]

) -> List[PersonType]:
    records = await select_person_types(start, limit)
    return BookingsFactory.get_person_types(records)


@router.post("/person-type", status_code=201, tags=["Unfinished"])
async def create_person(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:person-types"])
        ],
        person: PersonType
) -> PersonType:
    await add_object(
        PersonTypesRecord(
            person_type=person.person_type,
            discount_amount=person.discount_amount
        )
    )

    record = await select_person_type(person.person_type)
    return BookingsFactory.get_person_type(record)


@router.patch("/person-type", status_code=201, tags=["Unfinished"])
async def update_person(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:person-types"])
        ],
        person: PersonType
):
    query = update(
        PersonTypesRecord
    ).values(
        person_type=person.person_type,
        discount_amount=person.discount_amount
    ).where(
        PersonTypesRecord.person_type_id == person.id
    )
    await execute_safely(query)

    record = await select_person_type(person.person_type)
    return BookingsFactory.get_person_type(record)


@router.delete("/person-type", status_code=204, tags=["Unfinished"])
async def delete_person(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:person-types"])
        ],
        person: PersonType
):
    query = delete(
        PersonTypesRecord
    ).where(
        PersonTypesRecord.person_type == person.person_type
    )
    await execute_safely(query)
