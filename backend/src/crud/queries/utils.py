from fastapi import HTTPException
from pymysql import IntegrityError, DataError

from src.crud.engine import async_session


async def add_object(record) -> None:
    try:
        async with async_session() as session:
            async with session.begin():
                session.add(record)
                await session.commit()
    except (IntegrityError, DataError) as e:
        code = e.orig.args[0]
        message = e.orig.args[1]
        raise HTTPException(status_code=422, detail=message)
