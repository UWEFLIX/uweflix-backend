from sqlalchemy import select

from src.crud.engine import async_session
from src.crud.models import ClubsRecord, CitiesRecord


async def select_leader_clubs(leader: int):
    query = select(
        ClubsRecord
    ).where(ClubsRecord.leader == leader)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.all()

            return {x.id: x for x in rows}


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
