import asyncio
from typing import Annotated, List
from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param, Path
from sqlalchemy import select, delete, and_
from src.crud.models import (
    RolesRecord, PermissionsRecord, RolePermissionsRecord, UserRolesRecord
)
from src.crud.queries.roles import (
    select_roles, update_role_query
)
from src.crud.queries.user import select_user_by_id
from src.crud.queries.utils import (
    add_object, execute_safely, add_objects
)
from src.schema.factories.role_factory import RoleFactory
from src.schema.factories.user_factory import UserFactory
from src.schema.users import User, Role, Permission
from src.security.security import get_current_active_user

router = APIRouter(prefix="/roles", tags=["Roles"])


async def _get_role_by_name(role_name: str) -> Role:
    query = select(
        RolesRecord, RolePermissionsRecord, PermissionsRecord
    ).outerjoin(
        RolePermissionsRecord,
        RolePermissionsRecord.role_id == RolesRecord.role_id
    ).outerjoin(
        PermissionsRecord,
        PermissionsRecord.permission_id == RolePermissionsRecord.permissions_id
    ).where(RolesRecord.role_name == role_name)

    _map = await select_roles(query)

    if not _map:
        raise HTTPException(status_code=404, detail="Role not found")

    roles = RoleFactory.get_roles(_map)
    return roles[0]


async def _get_role_by_id(role_id: int) -> Role:
    query = select(
        RolesRecord, RolePermissionsRecord, PermissionsRecord
    ).outerjoin(
        RolePermissionsRecord,
        RolePermissionsRecord.role_id == RolesRecord.role_id
    ).outerjoin(
        PermissionsRecord,
        PermissionsRecord.permission_id == RolePermissionsRecord.permissions_id
    ).where(RolesRecord.role_id == role_id)

    _map = await select_roles(query)

    if not _map:
        raise HTTPException(status_code=404, detail="Role not found")

    roles = RoleFactory.get_roles(_map)
    return roles[0]


async def _update_role(role: Role):
    delete_query = delete(
        RolePermissionsRecord
    ).where(RolePermissionsRecord.role_id == role.id)
    await execute_safely(delete_query)

    insert_queries = [
        RolePermissionsRecord(
            role_id=role.id,
            permissions_id=x.id
        ) for x in role.permissions
    ]
    await add_objects(insert_queries)


@router.get("/roles", status_code=200, tags=["Unfinished"])
async def get_roles(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:roles"])
        ],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)]
):
    query = select(
        RolesRecord, RolePermissionsRecord, PermissionsRecord
    ).outerjoin(
        RolePermissionsRecord,
        RolePermissionsRecord.role_id == RolesRecord.role_id
    ).outerjoin(
        PermissionsRecord,
        PermissionsRecord.permission_id == PermissionsRecord.permission_id
    ).where(
        RolesRecord.role_id >= start,
    )
    _map = await select_roles(query)
    return RoleFactory.get_roles(_map)[:limit]


@router.get("/role", status_code=200, tags=["Unfinished"])
async def get_role(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:roles"])
        ],
        role_name: str
) -> Role:
    return await _get_role_by_name(role_name)


@router.get("/role/id/{role_id}", status_code=200, tags=["Unfinished"])
async def get_role_by_id(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:roles"])
        ],
        role_id: int
) -> Role:
    return await _get_role_by_id(role_id)


@router.post("/role", status_code=201, tags=["Unfinished"])
async def create_role(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:roles"])
        ],
        role: Role
):
    role_record = RolesRecord(
        role_name=role.name
    )
    await add_object(role_record)
    _role = await _get_role_by_name(role.name)

    role.id = _role.id
    await _update_role(role)

    return await _get_role_by_name(role.name)


@router.patch("/role", status_code=201, tags=["Unfinished"])
async def update_role(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:roles"])
        ],
        role: Role
):
    tasks = [update_role_query(role), _update_role(role)]
    await asyncio.gather(*tasks)

    return await _get_role_by_name(role.name)


# @router.delete("/role", status_code=204, tags=["Unfinished"])
# async def delete_role(
#         current_user: Annotated[
#             User, Security(get_current_active_user, scopes=["write:roles"])
#         ],
#         role: Role
# ):
#     role_record = RolesRecord(
#         role_id=role.id,
#         role_name=role.name
#     )
#     await delete_record(role_record)
#     return


@router.post("/user-role", status_code=201, tags=["Unfinished"])
async def append_user_role(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:roles"])
        ],
        user_id: int, role_id: int
) -> List[Role]:

    role_record = UserRolesRecord(
        role_id=role_id,
        user_id=user_id
    )

    await add_object(role_record)

    data = await select_user_by_id(user_id)
    user = UserFactory.create_full_user(data)

    return user.roles


@router.delete("/user-role", status_code=200, tags=["Unfinished"])
async def append_user_role(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:roles"])
        ],
        user_id: int, role_id: int
) -> List[Role]:

    query = delete(
        UserRolesRecord
    ).where(
        and_(
            UserRolesRecord.role_id == role_id,
            UserRolesRecord.user_id == user_id
        )
    )

    await execute_safely(query)

    data = await select_user_by_id(user_id)
    user = UserFactory.create_full_user(data)

    return user.roles


@router.post("/role-permission", status_code=201, tags=["Unfinished"])
async def append_user_role(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:roles"])
        ],
        permissions: List[Permission],
        role_id: Annotated[int, Param(title="role_id", ge=1)]
) -> Role:
    records = [
        RolePermissionsRecord(
            role_id=role_id,
            permissions_id=x.id
        ) for x in permissions
    ]

    await add_objects(records)

    return await _get_role_by_id(role_id)


@router.delete("/role-permission", status_code=200, tags=["Unfinished"])
async def append_user_role(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:roles"])
        ],
        permission_id: int, role_id: int
) -> Role:

    query = delete(
        RolePermissionsRecord
    ).where(
        and_(
            RolePermissionsRecord.role_id == role_id,
            RolePermissionsRecord.permissions_id == permission_id
        )
    )

    await execute_safely(query)

    return await _get_role_by_id(role_id)
