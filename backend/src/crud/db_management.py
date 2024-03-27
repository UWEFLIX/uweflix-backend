import asyncio
import aiomysql
from sqlalchemy import select

from src.crud.engine import engine, Base, async_session
from src.crud.models import PermissionsRecord, RolesRecord, RolePermissionsRecord
from src.crud.queries.utils import add_object


async def initialise_db():
    async with engine.begin() as connection:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        
    write_user = PermissionsRecord(permission="write:user")
    read_user = PermissionsRecord(permission="read:user")
    write_bookings = PermissionsRecord(permission="write:bookings")
    read_bookings = PermissionsRecord(permission="read:bookings")
    admin = RolesRecord(role_name="admin")
    admin_perm1 = RolePermissionsRecord(role_id=1, permissions_id=1)
    admin_perm2 = RolePermissionsRecord(role_id=1, permissions_id=2)

    await add_object(admin)

    objs = [write_user, read_user, write_bookings, read_bookings]

    tasks = [add_object(x) for x in objs]
    await asyncio.gather(*tasks)
    await asyncio.gather(*[
        add_object(admin_perm1), add_object(admin_perm2)
    ])

    # query = select(
    #     RolesRecord, RolePermissionsRecord, PermissionsRecord
    # ).join(
    #     RolePermissionsRecord, RolePermissionsRecord.role_id == RolesRecord.role_id
    # ).join(
    #     PermissionsRecord, PermissionsRecord.permission_id == RolePermissionsRecord.permission_id
    # ).where(
    #     RolesRecord.role_id == 1
    # )
    query = select(
        RolesRecord, RolePermissionsRecord, PermissionsRecord
    ).join(
        RolePermissionsRecord, RolesRecord.role_id == RolePermissionsRecord.role_id
    ).join(
        PermissionsRecord, RolePermissionsRecord.permissions_id == PermissionsRecord.permission_id
    ).where(
        RolesRecord.role_id == 1
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            records = result.fetchall()

            for record in records:
                role_record, role_permission_record, permission_record = record
                print(role_record.permissions)
                print(role_record.role_name)
                print(permission_record.permission)


async def close_db():
    await engine.dispose()
