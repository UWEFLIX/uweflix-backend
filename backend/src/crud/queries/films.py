from sqlalchemy import select

from src.crud.engine import async_session
from src.crud.models import HallsRecord


async def select_hall(hall_name: str):
    query = select(
        HallsRecord
    ).where(
        HallsRecord.hall_name == hall_name
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalar()


async def select_halls(start: int, limit: int):
    query = select(
        HallsRecord
    ).where(
        HallsRecord.hall_id >= start
    ).limit(limit)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars().all()
