import asyncio
from typing import Annotated
from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from pydantic import EmailStr
from sqlalchemy import delete, and_, update
from src.crud.models import (
    UsersRecord, AccountsRecord
)
from src.crud.queries.user import select_user_by_email, select_users
from src.crud.queries.utils import add_object, execute_safely
from src.endpoints.accounts.accounts import get_initials, update_club_account_uid
from src.schema.factories.user_factory import UserFactory
from src.schema.users import User
from src.security.security import get_current_active_user
from src.endpoints.users.passwords import router as passwords
from src.endpoints.users.roles import router as roles

router = APIRouter(prefix="/users", tags=["Users"])
router.include_router(passwords)
router.include_router(roles)


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
    user = UserFactory.create_full_user(user_record)

    accounts_record = AccountsRecord(
        account_uid=f"U{current_user.id}#{get_initials(user.name)}",
        name=user.name,
        entity_type="USER",
        entity_id=user.id,
        discount_rate=0
    )
    await add_object(accounts_record)

    coro = update_club_account_uid(user.name, current_user.id, "USER")
    asyncio.create_task(coro)

    return user


@router.patch("/user", status_code=201, tags=["Unfinished"])
async def update_user(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        new_name: str
) -> User:

    query = update(
        UsersRecord
    ).values(
        name=new_name,
        # status=user.status
    ).where(
        UsersRecord.email == current_user.email
    )

    _accounts_update = update(
        AccountsRecord
    ).values(
        account_uid=f"U{current_user.id}#{get_initials(new_name)}"
    ).where(
        and_(
            AccountsRecord.entity_id == current_user.id,
            AccountsRecord.entity_type == "USER"
        )
    )
    tasks = [
        execute_safely(query),
        update_club_account_uid(new_name, current_user.id, "USER")
    ]

    await asyncio.gather(*tasks)

    user_record = await select_user_by_email(current_user.email)
    return UserFactory.create_full_user(user_record)


@router.delete("/user", status_code=204, tags=["Unfinished"])
async def delete_user(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:users"])
        ],
        user_id: int
):
    query = delete(
        UsersRecord
    ).where(
        UsersRecord.user_id == user_id
    )
    await execute_safely(query)

    delete_accounts = delete(
        AccountsRecord
    ).where(
        and_(
            AccountsRecord.entity_id == user_id,
            AccountsRecord.entity_type == "USER"
        )
    )
    await execute_safely(delete_accounts)


# todo patch method to soft delete
