from sqlalchemy import select, and_

from src.crud.engine import async_session
from src.crud.models import HallsRecord, FilmsRecord, FilmImagesRecord, SchedulesRecord


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


async def select_film(title: str):
    query = select(
        FilmsRecord, FilmImagesRecord
    ).outerjoin(
        FilmImagesRecord, FilmImagesRecord.film_id == FilmsRecord.film_id
    ).where(
        FilmsRecord.title == title
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.all()

            if len(rows) == 0:
                return

            film = rows[0][0]
            images = [row[1] for row in rows if row[1]]

            return {
                "film": film,
                "images": images
            }


async def select_films(start: int, limit: int):
    query = select(
        FilmsRecord
    ).where(
        FilmsRecord.film_id >= start
    ).limit(limit)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars().all()


async def select_last_schedule(show_time, hall_id):
    query = select(
        SchedulesRecord, FilmsRecord
    ).join(
        FilmsRecord.film_id == SchedulesRecord.film_id
    ).where(
        and_(
            SchedulesRecord.show_time == show_time,
            SchedulesRecord.hall_id == hall_id
        )
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.all()
