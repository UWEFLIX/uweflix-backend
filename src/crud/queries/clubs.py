from sqlalchemy import select, asc, and_
from sqlalchemy.orm import aliased

from src.crud.engine import async_session
from src.crud.models import (
    ClubsRecord, CitiesRecord, ClubMembersRecords, UsersRecord, AccountsRecord, CardsRecord
)
from src.crud.queries.utils import scalar_selection


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
    query = select(
        CitiesRecord
    ).where(
        CitiesRecord.city_name == city_name
    )
    return await scalar_selection(query)


async def select_city_by_id(city_id: int):
    query = select(
        CitiesRecord
    ).where(
        CitiesRecord.city_id == city_id
    )
    return await scalar_selection(query)


async def select_club_by_id(club_id: int):
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
        ClubsRecord.id == club_id
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


async def select_cities(start, limit):
    query = select(
        CitiesRecord
    ).where(
        CitiesRecord.city_id >= start
    ).limit(
        limit
    ).order_by(asc(CitiesRecord.city_id))

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
    ).limit(limit).order_by(asc(ClubsRecord.id))

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.all()


async def select_club_members(club_id: int):
    members_query = select(
        ClubMembersRecords
    ).where(
        ClubMembersRecords.club == club_id
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(members_query)
            return result.scalars()


async def select_club_with_accounts(account_id: int):
    MemberRecords = aliased(UsersRecord)
    query = select(
        AccountsRecord, ClubsRecord, CitiesRecord, UsersRecord, MemberRecords,
        CardsRecord
    ).join(
        ClubsRecord, ClubsRecord.id == AccountsRecord.entity_id
    ).join(
        UsersRecord, UsersRecord.user_id == ClubsRecord.leader
    ).join(
        CitiesRecord, ClubsRecord.city_id == CitiesRecord.city_id
    ).outerjoin(
        ClubMembersRecords, ClubMembersRecords.club == ClubsRecord.id
    ).outerjoin(
        MemberRecords, MemberRecords.user_id == ClubMembersRecords.member
    ).outerjoin(
        CardsRecord, CardsRecord.account_id == AccountsRecord.id
    ).where(
        and_(
            AccountsRecord.id == account_id,
            AccountsRecord.entity_type == "CLUB"
        )
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.all()

            if len(rows) == 0:
                return None

            # AccountsRecord, ClubsRecord, CitiesRecord, UsersRecord, MemberRecords,
            # CardsRecord

            return {
                "club": rows[0][1],
                "city": rows[0][2],
                "leader": rows[0][3],
                "members": [x[4] for x in rows if x[4]],
                "account": rows[0][0],
                "cards": [x[5] for x in rows if x[5]],
            }
