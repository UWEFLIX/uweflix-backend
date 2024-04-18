from sqlalchemy import select
from sqlalchemy.orm import aliased

from src.crud.engine import async_session
from src.crud.models import (
    ClubsRecord, CitiesRecord, ClubMembersRecords, UsersRecord
)


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
    MemberRecords = aliased(UsersRecord)
    query = select(
        ClubsRecord, CitiesRecord, UsersRecord, MemberRecords
    ).join(
        UsersRecord, UsersRecord.user_id == ClubsRecord.leader
    ).join(
        CitiesRecord, ClubsRecord.city_id == CitiesRecord.city_id
    ).outerjoin(
        ClubMembersRecords, ClubMembersRecords.club == ClubsRecord.id
    ).outerjoin(
        MemberRecords, MemberRecords.user_id == ClubMembersRecords.member
    ).where(
        ClubsRecord.club_name == club_name
    )

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
                "members": [x[3] for x in rows if x[3]]
            }


async def select_clubs(start, limit):
    query = select(
        ClubsRecord, CitiesRecord
    ).join(
        CitiesRecord, CitiesRecord.city_id == ClubsRecord.city_id
    ).where(
        ClubsRecord.id >= start
    ).limit(limit)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.all()
