from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.engine import async_session
from src.crud.models import PersonTypesRecord


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
