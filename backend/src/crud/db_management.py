import asyncio

from sqlalchemy import select

from src.crud.engine import engine, Base, async_session
from src.crud.models import PermissionsRecord, RolesRecord, RolePermissionsRecord, UsersRecord, UserRolesRecord
from src.crud.queries.utils import add_object


async def initialise_db():
    async with engine.begin() as connection:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        
    write_user = PermissionsRecord(permission="write:user")
    read_user = PermissionsRecord(permission="read:user")
    write_bookings = PermissionsRecord(permission="write:bookings")
    read_bookings = PermissionsRecord(permission="read:bookings")
    read_hall = PermissionsRecord(permission="read:hall")
    write_hall = PermissionsRecord(permission="write:hall")

    admin = RolesRecord(role_name="admin")
    student = RolesRecord(role_name="student")

    admin_perm1 = RolePermissionsRecord(role_id=1, permissions_id=1)
    admin_perm2 = RolePermissionsRecord(role_id=1, permissions_id=2)
    student_perm1 = RolePermissionsRecord(role_id=2, permissions_id=3)
    student_perm2 = RolePermissionsRecord(role_id=2, permissions_id=4)
    user1 = UsersRecord(
        name="Nishawl Naseer",
        email="nishawl.naseer@outlook.com",
        password="$12$wg170NzRjZFAtCv0GQs80ObIPW2jTQnaWvsYRjl2iF5pSnRW6yLC."
    )
    user_role1 = UserRolesRecord(user_id=1, role_id=1)
    user_role2 = UserRolesRecord(user_id=1, role_id=2)

    await add_object(admin)
    await add_object(student)

    objs = [
        write_user, read_user, write_bookings,
        read_bookings, user1, read_hall, write_hall
    ]

    tasks = [add_object(x) for x in objs]
    await asyncio.gather(*tasks)

    objs2 = [
        student_perm1, student_perm2, admin_perm1, admin_perm2,
        user_role1, user_role2
    ]
    tasks2 = [add_object(x) for x in objs2]
    await asyncio.gather(*tasks2)

    query = select(
        UsersRecord, UserRolesRecord, RolesRecord, RolePermissionsRecord, PermissionsRecord
    ).join(
        UserRolesRecord, UserRolesRecord.user_id == UsersRecord.user_id
    ).join(
        RolesRecord, UserRolesRecord.role_id == RolesRecord.role_id
    ).join(
        RolePermissionsRecord, RolePermissionsRecord.role_id == RolesRecord.role_id
    ).join(
        PermissionsRecord, PermissionsRecord.permission_id == RolePermissionsRecord.permissions_id
    ).where(UsersRecord.user_id == 1)

    permissions_map = {}
    roles_map = {}
    user_roles_map = {}

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.all()

            user_record = rows[0][0]

            for row in rows:

                user_role_record = row[1]
                role_record = rows[2]
                permissions_record = rows[3]

                permissions_map[permissions_record.permission_id] = permissions_record
                roles_map[role_record.role_id] = role_record
                user_roles_map[user_role_record.id] = user_role_record

            lllll = {
                "user": user_record,
                "roles": roles_map,
                "permissions": permissions_map,
                "user_roles": user_roles_map
            }


async def close_db():
    await engine.dispose()
