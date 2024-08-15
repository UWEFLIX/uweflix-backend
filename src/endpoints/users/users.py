import asyncio
from typing import Annotated, List
from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from pydantic import EmailStr
from sqlalchemy import delete, and_, update, select
from src.crud.models import (
    UsersRecord, AccountsRecord, UserRolesRecord
)
from src.crud.queries.user import select_user_by_email, select_users, select_user_by_id
from src.crud.queries.utils import add_object, execute_safely, add_objects, scalar_selection, scalars_selection
from src.endpoints.accounts.accounts import get_initials, update_club_account_uid
from src.schema.factories.user_factory import UserFactory
from src.schema.users import User
from src.security.security import get_current_active_user
from src.endpoints.users.passwords import router as passwords
from src.endpoints.users.roles import router as roles

router = APIRouter(prefix="/users", tags=["Users"])
router.include_router(passwords)
router.include_router(roles)


async def _update_roles(user: User):
    if user.roles is None:
        return

    delete_query = delete(UserRolesRecord).where(UserRolesRecord.user_id == user.id)
    await execute_safely(delete_query)

    insert_queries = [
        UserRolesRecord(
            role_id=x.id,
            user_id=user.id
        ) for x in user.roles
    ]
    await add_objects(insert_queries)


@router.get("/user", status_code=200, tags=["Unfinished"])
async def get_user(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:users"])
        ],
        email: EmailStr
) -> User:
    user_record = await select_user_by_email(email)
    if not user_record:
        raise HTTPException(404, "User not found")

    return UserFactory.create_full_user(user_record)


@router.get("/user/id/{user_id}/", status_code=200, tags=["Unfinished"])
async def get_user_by_id(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:users"])
        ],
        user_id: int
) -> User:
    user_record = await select_user_by_id(user_id)
    if not user_record:
        raise HTTPException(404, "User not found")

    return UserFactory.create_full_user(user_record)


@router.get("/users", status_code=200, tags=["Unfinished"])
async def get_users(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:users"])
        ],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)]
) -> list[User]:
    user_records = await select_users(start, limit)

    return UserFactory.create_half_users(user_records)


@router.post("/user", status_code=201, tags=["Unfinished"])
async def create_user(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:users"])
        ],
        user: User
) -> User:
    record = UsersRecord(
        name=user.name,
        email=user.email,
        status="ENABLED"
    )
    await add_object(record)

    user_record = await select_user_by_email(user.email)
    _user = UserFactory.create_full_user(user_record)

    user.id = _user.id
    await _update_roles(user)

    user_record = await select_user_by_email(user.email)
    user = UserFactory.create_full_user(user_record)

    accounts_record = AccountsRecord(
        account_uid=f"U{current_user.id}#{get_initials(user.name)}",
        name=user.name,
        entity_type="USER",
        entity_id=user.id,
        discount_rate=0,
        status="ENABLED"
    )
    await add_object(accounts_record)

    coro = update_club_account_uid(user.name, user.id, "USER")
    asyncio.create_task(coro)

    return user


@router.patch("/user", status_code=201, tags=["Unfinished"])
async def update_user(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        user: User
) -> User:
    query = update(
        UsersRecord
    ).values(
        name=user.name,
        # status=user.status
    ).where(
        UsersRecord.user_id == user.id
    )

    _accounts_update = update(
        AccountsRecord
    ).values(
        account_uid=f"U{current_user.id}#{get_initials(user.name)}"
    ).where(
        and_(
            AccountsRecord.entity_id == current_user.id,
            AccountsRecord.entity_type == "USER"
        )
    )
    tasks = [
        execute_safely(query),
        update_club_account_uid(user.name, user.id, "USER"),
        _update_roles(user)
    ]

    await asyncio.gather(*tasks)

    user_record = await select_user_by_email(user.email)
    return UserFactory.create_full_user(user_record)


@router.get("/users/{string}/", status_code=201)
async def get_users(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        string: str
):
    query = select(
        UsersRecord
    )
    records: List[UsersRecord] = await scalars_selection(query)

    users = []
    string = string.lower()
    for record in records:
        if string in record.name.lower() or \
                string in record.email.lower():
            users.append(
                UserFactory.create_half_user(record)
            )

    return users
