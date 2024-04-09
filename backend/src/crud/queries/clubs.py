from sqlalchemy import select

from src.crud.engine import async_session
from src.crud.models import ClubsRecord, CitiesRecord, ClubMemberRecords, UsersRecord


async def select_leader_clubs(leader: int):
    query = select(
        ClubsRecord
    ).where(ClubsRecord.leader == leader)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.all()

            return {x[0].id: x for x in rows}


async def select_city(city_name: str):
    async with async_session() as session:
        async with session.begin():
            query = select(
                CitiesRecord
            ).where(
                CitiesRecord.city_name == city_name
            )

            result = await session.execute(query)
            return result.scalar()


async def select_cities(start, limit):
    query = select(
        CitiesRecord
    ).where(
        CitiesRecord.city_id >= start
    ).limit(
        limit
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            return result.scalars().all()


async def select_club(club_name: str):
    query = (select(
        ClubsRecord, CitiesRecord, UsersRecord, UsersRecord
    ).join(
        UsersRecord, UsersRecord.id == ClubsRecord.leader
    ).join(
        ClubsRecord, ClubsRecord.city_id == CitiesRecord.city_id
    ).outerjoin(
        ClubMemberRecords, ClubMemberRecords.club == ClubsRecord.id
    ).outerjoin(
        UsersRecord, UsersRecord.id == ClubMemberRecords.member
    ).where(
        ClubsRecord.club_name == club_name
    ))

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.all()

            if len(rows) == 0:
                return None

            return {
                "club": rows[0][0],
                "city": rows[0][1],
                "leader": rows[0][2],
                "members": [x for x in rows[0][3] if x]
            }
