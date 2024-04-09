from fastapi import HTTPException
from sqlalchemy import select, update, and_
from sqlalchemy.exc import DataError, IntegrityError

from src.crud.engine import async_session
from src.crud.models import RolesRecord, RolePermissionsRecord, PermissionsRecord, UsersRecord, UserRolesRecord
from src.crud.queries.utils import execute_safely
from src.schema.users import Role


async def select_roles(
        query=select(
        RolesRecord, RolePermissionsRecord, PermissionsRecord
        ).outerjoin(
            RolePermissionsRecord,
            RolePermissionsRecord.role_id == RolesRecord.role_id
        ).outerjoin(
            PermissionsRecord,
            PermissionsRecord.permission_id == PermissionsRecord.permission_id
        )
):
    permissions = {}
    roles = {}
    user_roles = {}
    role_permissions = {}

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            if not result:
                return

            rows = result.all()

            if len(rows) == 0:
                return
            elif len(rows) == 1:
                if not rows[0][1]:
                    record = rows[0][0]
                    roles.update({record.role_id: record})
                    return {
                        "roles": roles,
                        "permissions": permissions,
                        "user_roles": user_roles,
                        "role_permissions": role_permissions
                    }

            for row in rows:
                # UsersRecord, UserRolesRecord, RolesRecord, RolePermissionsRecord,
                # PermissionsRecord
                role_record = row[0]
                role_permissions_record = row[1]
                permissions_record = row[2]

                roles.update({role_record.role_id: role_record})
                permissions.update({
                    permissions_record.permission_id: permissions_record
                })
                role_permissions.update({
                    role_permissions_record.id: role_permissions_record
                })

    return {
        "roles": roles,
        "permissions": permissions,
        "user_roles": user_roles,
        "role_permissions": role_permissions
    }


async def update_role(role: Role):
    query = update(
        RolesRecord
    ).values(
        role_name=role.role_name,
    ).where(
        RolesRecord.role_id == role.role_id
    )
    await execute_safely(query)


async def get_user_role_data(username: str, role_name: str):
    query = select(
        UsersRecord, RolesRecord
    ).where(
        and_(
            UsersRecord.email == username,
            RolesRecord.role_name == role_name
        )
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars().all()



