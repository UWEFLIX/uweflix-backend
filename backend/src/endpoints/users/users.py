from typing import Annotated, List

from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from pydantic import EmailStr
from sqlalchemy import select, delete, and_, update

from src.crud.models import (
    RolesRecord, PermissionsRecord, RolePermissionsRecord, UserRolesRecord, UsersRecord, AccountsRecord
)
from src.crud.queries.roles import (
    select_roles
)
from src.crud.queries.user import select_user_by_id, select_user_by_email, select_users
from src.crud.queries.utils import add_object, delete_record, execute_safely, add_objects
from src.schema.factories.role_factory import RoleFactory
from src.schema.factories.user_factory import UserFactory
from src.schema.users import User, Role, Permission
from src.security.security import get_current_active_user
from src.endpoints.users.passwords import router as passwords

router = APIRouter(prefix="/users", tags=["Users"])
router.include_router(passwords)


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
    return UserFactory.create_full_user(user_record)


@router.patch("/user", status_code=201, tags=["Unfinished"])
async def update_user(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        user: User
) -> User:

    # query = update(UsersRecord)

    if current_user.email != user.email:
        if "write:users" not in current_user.permissions:
            raise HTTPException(
                403, "Forbidden"
            )
        query = update(
            UsersRecord
        ).values(
            name=user.name,
            status=user.status
        ).where(
            UsersRecord.email == user.email
        )
    else:
        query = update(
            UsersRecord
        ).values(
            name=user.name,
            # status=user.status
        ).where(
            UsersRecord.email == user.email
        )

    # query.where(
    #     UsersRecord.email == user.email
    # )
    await execute_safely(query)

    user_record = await select_user_by_email(user.email)
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

