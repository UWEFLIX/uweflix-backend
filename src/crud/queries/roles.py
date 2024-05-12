from sqlalchemy import select, update, and_, asc
from src.crud.engine import async_session
from src.crud.models import (
    RolesRecord, UsersRecord
)
from src.crud.queries.utils import execute_safely
from src.schema.users import Role


async def select_roles(
        query
):
    permissions = {}
    roles = {}
    user_roles = {}
    role_permissions = {}

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query.order_by(asc(RolesRecord.role_id)))

            if not result:
                return

            rows = result.all()

            # if len(rows) == 0:
            #     return
            # elif len(rows) == 1:
            #     if not rows[0][1]:
            #         record = rows[0][0]
            #         roles.update({record.role_id: record})
            #         return {
            #             "roles": roles,
            #             "permissions": permissions,
            #             "user_roles": user_roles,
            #             "role_permissions": role_permissions
            #         }

            for row in rows:
                # UsersRecord, UserRolesRecord, RolesRecord, RolePermissionsRecord,
                # PermissionsRecord
                role_record = row[0]
                role_permissions_record = row[1]
                permissions_record = row[2]

                if role_record:
                    roles.update({role_record.role_id: role_record})

                if permissions_record:
                    permissions.update({
                        permissions_record.permission_id: permissions_record
                    })

                if role_permissions_record:
                    role_permissions.update({
                        role_permissions_record.id: role_permissions_record
                    })

    return {
        "roles": roles,
        "permissions": permissions,
        "user_roles": user_roles,
        "role_permissions": role_permissions
    }


async def update_role_query(role: Role):
    query = update(
        RolesRecord
    ).values(
        role_name=role.name,
    ).where(
        RolesRecord.role_id == role.id
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
