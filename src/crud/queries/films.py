from datetime import datetime

from sqlalchemy import select, and_, asc

from src.crud.engine import async_session
from src.crud.models import (
    HallsRecord, FilmsRecord, FilmImagesRecord, SchedulesRecord
)


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
    ).limit(limit).order_by(asc(HallsRecord.hall_id))

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


async def select_film_by_id(film_id: int):
    query = select(
        FilmsRecord, FilmImagesRecord
    ).outerjoin(
        FilmImagesRecord, FilmImagesRecord.film_id == FilmsRecord.film_id
    ).where(
        FilmsRecord.film_id == film_id
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
    ).limit(limit).order_by(asc(FilmsRecord.film_id))

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


async def select_images(film_id: int, batch: int):
    query = select(
        FilmImagesRecord
    ).where(
        and_(
            FilmImagesRecord.film_id == film_id,
            FilmImagesRecord.batch == batch
        )
    ).order_by(asc(FilmImagesRecord.image_id))
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars().all()


async def select_film_schedules(query):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.all()

            if len(rows) == 0:
                return None

            film = rows[0][0]
            schedules = [
                x[1] for x in rows if x[1]
            ]
            return {
                "film": film,
                "schedules": schedules
            }


async def select_inserted_schedules(film_id: int, hall_id: int, show_time: str):
    query = select(
        SchedulesRecord, FilmsRecord, HallsRecord
    ).join(
        FilmsRecord, FilmsRecord.film_id == SchedulesRecord.film_id
    ).join(
        HallsRecord, HallsRecord.hall_id == SchedulesRecord.hall_id
    ).where(
        and_(
            FilmsRecord.film_id == film_id,
            HallsRecord.hall_id == hall_id,
            SchedulesRecord.show_time == show_time
        )
    ).order_by(asc(SchedulesRecord.schedule_id))

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            rows = result.fetchone()
            if not rows:
                return
            return [rows[0], rows[1], rows[2]]


async def select_schedule(schedule_id: int):
    query = select(
        SchedulesRecord, FilmsRecord, HallsRecord
    ).join(
        FilmsRecord, FilmsRecord.film_id == SchedulesRecord.film_id
    ).join(
        HallsRecord, HallsRecord.hall_id == SchedulesRecord.hall_id
    ).where(
        SchedulesRecord.schedule_id == schedule_id
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            rows = result.fetchone()
            if not rows:
                return
            return [rows[0], rows[1], rows[2]]


async def select_schedules(start: int, limit: int):
    query = select(
        SchedulesRecord, FilmsRecord, HallsRecord
    ).join(
        FilmsRecord, FilmsRecord.film_id == SchedulesRecord.film_id
    ).join(
        HallsRecord, HallsRecord.hall_id == SchedulesRecord.hall_id
    ).where(
        SchedulesRecord.schedule_id >= start
    ).limit(limit).order_by(asc(SchedulesRecord.schedule_id))
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            return result.all()


async def select_all_schedules():
    query = select(
        SchedulesRecord, FilmsRecord, HallsRecord
    ).join(
        FilmsRecord, FilmsRecord.film_id == SchedulesRecord.film_id
    ).join(
        HallsRecord, HallsRecord.hall_id == SchedulesRecord.hall_id
    ).order_by(asc(SchedulesRecord.schedule_id))
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            return result.all()


# async def select_film_by_id(film_id: int):
#     query = select(
#         FilmsRecord
#     ).where(
#         FilmsRecord.film_id == film_id
#     )
#
#     async with async_session() as session:
#         async with session.begin():
#             result = await session.execute(query)
#             return result.scalar()


async def select_schedules_by_hall_id(hall_id: int, limit: int):
    query = select(
        SchedulesRecord, FilmsRecord
    ).join(
        FilmsRecord, FilmsRecord.film_id == SchedulesRecord.film_id
    ).where(
        SchedulesRecord.hall_id == hall_id
    ).limit(limit).order_by(asc(SchedulesRecord.schedule_id))
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            return result.all()


async def select_hall_by_id(hall_id: int):
    query = select(
        HallsRecord
    ).where(
        HallsRecord.hall_id == hall_id
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalar()
