from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.models import PersonTypesRecord


async def select_person_type(person_type: str):
    query = select(
        PersonTypesRecord
    ).where(
        PersonTypesRecord.person_type == person_type
    )

    async with Session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalar()
