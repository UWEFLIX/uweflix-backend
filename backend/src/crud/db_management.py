import asyncio

from sqlalchemy import text

from src.crud.engine import engine, Base, async_session
from src.crud.models import (
    PermissionsRecord, RolesRecord, RolePermissionsRecord,
    UsersRecord, UserRolesRecord, AccountsRecord
)
from src.crud.queries.utils import add_object, add_objects
from src.crud.queries.stored_procedures import generate_unique_string, generate_filename


async def get_permissions():
    write_user = PermissionsRecord(permission="write:users")
    read_user = PermissionsRecord(permission="read:users")

    write_bookings = PermissionsRecord(permission="write:bookings")
    read_bookings = PermissionsRecord(permission="read:bookings")

    read_halls = PermissionsRecord(permission="read:halls")
    write_halls = PermissionsRecord(permission="write:halls")

    read_clubs = PermissionsRecord(permission="read:clubs")
    write_clubs = PermissionsRecord(permission="write:clubs")

    read_user_roles = PermissionsRecord(permission="read:user_roles")
    write_user_roles = PermissionsRecord(permission="write:user_roles")

    read_roles = PermissionsRecord(permission="read:roles")
    write_roles = PermissionsRecord(permission="write:roles")

    read_cities = PermissionsRecord(permission="read:cities")
    write_cities = PermissionsRecord(permission="write:cities")

    read_schedules = PermissionsRecord(permission="read:schedules")
    write_schedules = PermissionsRecord(permission="write:schedules")

    read_films = PermissionsRecord(permission="read:films")
    write_films = PermissionsRecord(permission="write:films")

    read_images = PermissionsRecord(permission="read:images")
    write_images = PermissionsRecord(permission="write:images")

    read_role_perms = PermissionsRecord(permission="read:role_permissions")
    write_role_perms = PermissionsRecord(permission="write:role_permissions")

    read_person_type = PermissionsRecord(permission="read:person-types")
    write_person_type = PermissionsRecord(permission="write:person-types")

    read_accounts = PermissionsRecord(permission="read:accounts")
    write_accounts = PermissionsRecord(permission="write:accounts")

    return [
        write_user, read_user, write_bookings, read_bookings,
        read_halls, write_halls, read_clubs, write_clubs,
        read_user_roles, write_user_roles, read_roles,
        write_roles, read_cities, write_cities, read_schedules,
        write_schedules, read_films, write_films, read_images,
        write_images, read_role_perms, write_role_perms,
        read_person_type, write_person_type, read_accounts,
        write_accounts
    ]


def admin_perms(count: int):
    return [
        RolePermissionsRecord(
            role_id=1, permissions_id=x+1
        ) for x in range(count)
    ]


async def initialise_db():

    async with async_session() as session:
        async with session.begin():
            await session.execute(text(generate_unique_string()))
            await session.execute(text(generate_filename()))

    async with engine.begin() as connection:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    objs = await get_permissions()

    admin = RolesRecord(role_name="admin")

    objs2: list = admin_perms(len(objs))
    user1 = UsersRecord(
        name="Nishawl Naseer",
        email="nishawl.naseer@outlook.com",
        password="$2b$12$qtCm88dd7JSa9SGlwKGp/e/VDEbZ0kbSmnUJEC7sgunD1whHFBjeW"
    )
    account1 = AccountsRecord(
        account_uid="2",
        name="Nishawl Naseer",
        entity_type="USER",
        entity_id=1,
        discount_rate=0,
        status="ENABLED"
    )
    user_role1 = UserRolesRecord(user_id=1, role_id=1)

    await add_object(admin)

    objs.append(user1)

    await add_objects(objs)

    # tasks = [add_object(x) for x in objs]
    # await asyncio.gather(*tasks)

    objs2.extend([user_role1, account1])
    tasks2 = [add_object(x) for x in objs2]
    await asyncio.gather(*tasks2)


async def close_db():
    await engine.dispose()
