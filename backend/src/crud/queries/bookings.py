from collections import defaultdict
from typing import Dict
from sqlalchemy import select, and_, text
from src.crud.engine import async_session
from src.crud.models import (
    PersonTypesRecord, BookingsRecord, SchedulesRecord, HallsRecord, FilmsRecord,
    AccountsRecord, UsersRecord
)
from src.crud.queries.raw_sql import (
    select_batch_data, club_pre_booking_details, user_pre_booking_details
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
    query = select_batch_data

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(text(query))
            rows = result.fetchall()

    return {
        batch_ref: BatchData(
            batch_ref=batch_ref,
            count=count,
            created=created,
            total=total
        ) for batch_ref, created, count, total in rows
    }


async def get_details(entity_id: int, entity_type: str, schedule_id: int):
    values = (schedule_id, entity_id,)
    if entity_type == "CLUB":
        query = club_pre_booking_details % values
    else:
        query = user_pre_booking_details % values

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(text(query))

            details = defaultdict(dict)
            rows = result.fetchall()

            schedule_record = SchedulesRecord(
                schedule_id=rows[0][11],
                hall_id=rows[0][12],
                film_id=rows[0][13],
                show_time=rows[0][14],
                on_schedule=rows[0][15],
                ticket_price=rows[0][16],
            )
            hall_record = HallsRecord(
                hall_id=rows[0][17],
                hall_name=rows[0][18],
                seats_per_row=rows[0][19],
                no_of_rows=rows[0][20],
            )

            for row in rows:
                person_id = row[8]
                if person_id:
                    person_type = PersonTypesRecord(
                        person_type_id=person_id,
                        person_type=[9],
                        discount_amount=[10],
                    )
                    details["persons"][person_id] = person_type

                if entity_type == "CLUB":
                    member_id = row[24]
                    email = row[26]
                    if member_id:
                        member = UsersRecord(
                            user_id=member_id,
                            name=row[25],
                            email=email,
                            password=row[27],
                            status=row[28],
                        )
                        details["club_members"][email] = member

                account_record = AccountsRecord(
                    id=row[0],
                    account_uid=row[1],
                    name=row[2],
                    entity_type=row[3],
                    entity_id=row[4],
                    discount_rate=row[5],
                    status=row[6],
                    balance=row[7],
                )
                details["accounts"][account_record.id] = account_record
                # account_record = row[0]
                # persons_record = row[1]
                # schedule_record = row[2]
                # hall_record = row[3]
                #
                # if account_record:
                #     details["accounts"][account_record.id] = account_record
                #
                # if persons_record:
                #     details["persons"][persons_record.person_type_id] = \
                #         persons_record
                #
                # if schedule_record:
                #     details["schedules"] = schedule_record
                #     details["halls"] = hall_record
                #
                # if entity_type == "CLUB":
                #     club_member_record = row[4]
                #     if club_member_record:
                #         details["club_members"][club_member_record.email] = True

    details["schedules"] = schedule_record
    details["halls"] = hall_record
    details["batches"] = await select_batches()
    return details


async def select_batch(batch: str):
    query = select(
        BookingsRecord, SchedulesRecord, FilmsRecord, HallsRecord,
        AccountsRecord, PersonTypesRecord
    ).join(
        SchedulesRecord,
        SchedulesRecord.schedule_id == BookingsRecord.schedule_id
    ).join(
        FilmsRecord,
        SchedulesRecord.film_id == FilmsRecord.film_id
    ).join(
        HallsRecord,
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


async def select_assigned_bookings(email: str):
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
        BookingsRecord.assigned_user == email
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.fetchall()

