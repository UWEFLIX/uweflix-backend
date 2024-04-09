from sqlalchemy import select

from src.crud.engine import async_session
from src.crud.models import ClubsRecord


async def select_leader_clubs(leader: int):
    query = select(
        ClubsRecord
    ).where(ClubsRecord.leader == leader)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.all()

            return {x.id: x for x in rows}
