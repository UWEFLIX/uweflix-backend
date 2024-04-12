from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.engine import async_session
from src.crud.models import PersonTypesRecord, BookingsRecord, SchedulesRecord, HallsRecord, FilmsRecord, AccountsRecord


async def select_person_type(person_type: str):
    query = select(
        PersonTypesRecord
    ).where(
        PersonTypesRecord.person_type == person_type
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalar()


async def select_person_types(start, limit):
    query = select(
        PersonTypesRecord
    ).where(
        PersonTypesRecord.person_type_id >= start
    ).limit(limit)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars().all()


async def select_booking(booking_id: int):
    query = select(
        BookingsRecord, SchedulesRecord, FilmsRecord, HallsRecord,
        AccountsRecord, PersonTypesRecord
    ).join(
        SchedulesRecord.schedule_id == BookingsRecord.schedule_id
    ).join(
        SchedulesRecord.film_id == FilmsRecord.film_id
    ).join(
        HallsRecord.hall_id == SchedulesRecord.hall_id
    ).join(
        AccountsRecord, AccountsRecord.id == BookingsRecord.account_id
    ).join(
        PersonTypesRecord,
        PersonTypesRecord.person_type_id == BookingsRecord.person_type_id
    ).where(
        BookingsRecord.booking_id == booking_id
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            row = result.fetchone()
            return row
