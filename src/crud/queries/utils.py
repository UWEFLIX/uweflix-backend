from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, DataError

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


async def execute_safely(query):
    async with async_session() as session:
        async with session.begin():
            try:
                await session.execute(query)
            except (DataError, IntegrityError) as e:
                raise HTTPException(status_code=422, detail=e.orig.args[1])

            await session.commit()


async def delete_record(record):
    async with async_session() as session:
        async with session.begin():
            try:
                await session.delete(record)
            except (DataError, IntegrityError) as e:
                raise HTTPException(status_code=422, detail=e.orig.args[1])


async def add_objects(records) -> None:
    try:
        async with async_session() as session:
            async with session.begin():
                session.add_all(records)
                await session.commit()
    except (IntegrityError, DataError) as e:
        code = e.orig.args[0]
        message = e.orig.args[1]
        raise HTTPException(status_code=422, detail=message)


async def scalar_selection(query):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalar()


async def scalars_selection(query):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars()


async def all_selection(query):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.all()
