from sqlalchemy import select

from src.crud.engine import async_session
from src.crud.models import (
    UsersRecord, UserRolesRecord, RolesRecord, RolePermissionsRecord,
    PermissionsRecord
)


async def select_user_by_email(username: str) -> dict | None:
    query = select(
        UsersRecord, UserRolesRecord, RolesRecord, RolePermissionsRecord,
        PermissionsRecord
    ).outerjoin(
        UserRolesRecord, UserRolesRecord.user_id == UsersRecord.user_id
    ).outerjoin(
        RolesRecord, UserRolesRecord.role_id == RolesRecord.role_id
    ).outerjoin(
        RolePermissionsRecord,
        RolePermissionsRecord.role_id == RolesRecord.role_id
    ).outerjoin(
        PermissionsRecord,
        PermissionsRecord.permission_id == RolePermissionsRecord.permissions_id
    ).where(UsersRecord.email == username)

    permissions = {}
    roles = {}
    user_roles = {}
    role_permissions = {}

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            rows = result.all()

            if len(rows) == 0:
                return None

            user_record = rows[0][0]

            for row in rows:
                # UsersRecord, UserRolesRecord, RolesRecord, RolePermissionsRecord, PermissionsRecord
                user_role_record = row[1]
                role_record = row[2]
                role_permissions_record = row[3]
                permissions_record = row[4]

                if role_record:
                    roles.update({role_record.role_id: role_record})
                if user_role_record:
                    user_roles.update({user_role_record.id: user_role_record})
                if permissions_record:
                    permissions.update({permissions_record.permission_id: permissions_record})
                if role_permissions_record:
                    role_permissions.update({role_permissions_record.id: role_permissions_record})

    return {
        "user": user_record,
        "roles": roles,
        "permissions": permissions,
        "user_roles": user_roles,
        "role_permissions": role_permissions
    }


async def select_user_by_id(user_id: int) -> dict | None:
    query = select(
        UsersRecord, UserRolesRecord, RolesRecord, RolePermissionsRecord,
        PermissionsRecord
    ).outerjoin(
        UserRolesRecord, UserRolesRecord.user_id == UsersRecord.user_id
    ).outerjoin(
        RolesRecord, UserRolesRecord.role_id == RolesRecord.role_id
    ).outerjoin(
        RolePermissionsRecord,
        RolePermissionsRecord.role_id == RolesRecord.role_id
    ).outerjoin(
        PermissionsRecord,
        PermissionsRecord.permission_id == RolePermissionsRecord.permissions_id
    ).where(UsersRecord.user_id == user_id)

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

            user_record = rows[0][0]

            for row in rows:
                # UsersRecord, UserRolesRecord, RolesRecord, RolePermissionsRecord, PermissionsRecord
                user_role_record = row[1]
                role_record = row[2]
                role_permissions_record = row[3]
                permissions_record = row[4]

                if role_record:
                    roles.update({role_record.role_id: role_record})
                if user_role_record:
                    user_roles.update({
                        user_role_record.id: user_role_record
                    })
                if permissions_record:
                    permissions.update({
                        permissions_record.permission_id: permissions_record
                    })
                if role_permissions_record:
                    role_permissions.update({
                        role_permissions_record.id: role_permissions_record
                    })

    return {
        "user": user_record,
        "roles": roles,
        "permissions": permissions,
        "user_roles": user_roles,
        "role_permissions": role_permissions
    }


async def select_users(start, limit):
    query = select(
        UsersRecord
    ).where(
        UsersRecord.user_id >= start
    ).limit(limit)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            return result.scalars().all()
