from sqlalchemy import select

from src.crud.engine import async_session
from src.crud.models import UsersRecord, UserRolesRecord, RolesRecord, RolePermissionsRecord, PermissionsRecord


async def select_user_by_email(username: str) -> dict | None:
    query = select(
        UsersRecord, UserRolesRecord, RolesRecord, RolePermissionsRecord,
        PermissionsRecord
    ).join(
        UserRolesRecord, UserRolesRecord.user_id == UsersRecord.user_id
    ).join(
        RolesRecord, UserRolesRecord.role_id == RolesRecord.role_id
    ).join(
        RolePermissionsRecord,
        RolePermissionsRecord.role_id == RolesRecord.role_id
    ).join(
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

                roles.update({role_record.role_id: role_record})
                user_roles.update({user_role_record.id: user_record})
                permissions.update({permissions_record.permission_id: permissions_record})
                role_permissions.update({role_permissions_record.id: role_permissions_record})

    return {
        "user": user_record,
        "roles": roles,
        "permissions": permissions,
        "user_roles": user_roles,
        "role_permissions": role_permissions
    }
