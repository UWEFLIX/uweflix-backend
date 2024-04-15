from collections import defaultdict
from typing import Dict
from sqlalchemy import select, and_, text
from src.crud.engine import async_session
from src.crud.models import (
    PersonTypesRecord, BookingsRecord, SchedulesRecord, HallsRecord, FilmsRecord,
    AccountsRecord, ClubMembersRecords, ClubsRecord, UsersRecord
)
from src.schema.bookings import BatchData


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


async def select_club_bookings(start: int, limit: int, club_id: int):
    query = select(
        BookingsRecord, SchedulesRecord, FilmsRecord, HallsRecord,
        AccountsRecord, PersonTypesRecord
    ).join(
        SchedulesRecord,
        SchedulesRecord.schedule_id == BookingsRecord.schedule_id
    ).join(
        FilmsRecord, SchedulesRecord.film_id == FilmsRecord.film_id
    ).join(
        HallsRecord, HallsRecord.hall_id == SchedulesRecord.hall_id
    ).join(
        AccountsRecord, AccountsRecord.id == BookingsRecord.account_id
    ).join(
        PersonTypesRecord,
        PersonTypesRecord.person_type_id == BookingsRecord.person_type_id
    ).where(
        and_(
            BookingsRecord.id >= start,
            AccountsRecord.entity_id == club_id,
            AccountsRecord.entity_type == "CLUB"
        )
    ).limit(limit)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.fetchall()


async def select_user_bookings(start: int, limit: int, user_id: int):
    query = select(
        BookingsRecord, SchedulesRecord, FilmsRecord, HallsRecord,
        AccountsRecord, PersonTypesRecord
    ).join(
        SchedulesRecord,
        SchedulesRecord.schedule_id == BookingsRecord.schedule_id
    ).join(
        FilmsRecord, SchedulesRecord.film_id == FilmsRecord.film_id
    ).join(
        HallsRecord, HallsRecord.hall_id == SchedulesRecord.hall_id
    ).join(
        AccountsRecord, AccountsRecord.id == BookingsRecord.account_id
    ).join(
        PersonTypesRecord,
        PersonTypesRecord.person_type_id == BookingsRecord.person_type_id
    ).where(
        and_(
            BookingsRecord.id >= start,
            AccountsRecord.entity_id == user_id,
            AccountsRecord.entity_type == "USER"
        )
    ).limit(limit)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.fetchall()


async def select_batches() -> Dict[str, BatchData]:
    table_name = BookingsRecord.__tablename__
    query = f"""
        SELECT 
            `batch_ref`, 
            MIN(`created`) AS first_datetime,
            COUNT(*) AS occurrences,
            SUM(`amount`) AS total_amount
        FROM 
            {table_name}
        GROUP BY 
            `batch_ref`;
    """

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(text(query))
            rows = result.fetchall()
            return {
                batch_ref: BatchData(
                    batch_ref=batch_ref,
                    count=count,
                    created=created,
                    total=total,
                )
                for batch_ref, created, count, total in rows
            }


async def get_details(entity_id: int, entity_type: str, schedule_id: int):
    tables = [AccountsRecord, PersonTypesRecord, SchedulesRecord, HallsRecord]

    if entity_type == "CLUB":
        tables.extend([UsersRecord])

    query = select(
        *tables
        # FilmsRecord
    ).outerjoin(
        PersonTypesRecord, PersonTypesRecord.person_type_id >= 1
    ).outerjoin(
        SchedulesRecord, SchedulesRecord.id == schedule_id
    ).outerjoin(
        HallsRecord, HallsRecord.hall_id == SchedulesRecord.hall_id
    )

    if entity_type == "CLUB":
        query = query.outerjoin(
            ClubMembersRecords, ClubMembersRecords.club == ClubsRecord.entity_id
        ).join(
            UsersRecord, UsersRecord.user_id == ClubMembersRecords.member
        )

    query = query.where(
        and_(
            AccountsRecord, AccountsRecord.entity_id == entity_id,
            AccountsRecord.entity_type == entity_type
        )
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            details = defaultdict(dict)
            rows = result.fetchall()
            for row in rows:
                account_record = row[0]
                persons_record = row[1]
                schedule_record = row[2]
                hall_record = row[3]

                if account_record:
                    details["accounts"][account_record.id] = account_record

                if persons_record:
                    details["persons"][persons_record.person_type_id] = \
                        persons_record

                if schedule_record:
                    details["schedules"] = schedule_record
                    details["halls"] = hall_record

                if entity_type == "CLUB":
                    club_member_record = row[4]
                    if club_member_record:
                        details["club_members"][club_member_record.email] = True

    details["batches"] = await select_batches()
    return details


async def select_batch(batch: str):
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
        BookingsRecord.batch_ref == batch
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.fetchall()

            if len(rows) == 0:
                return None
            return rows
