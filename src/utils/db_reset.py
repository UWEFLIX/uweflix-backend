import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.crud.db_management import initialise_db, close_db
from src.crud.drop import create_new_db


async def reset():
    await create_new_db()
    await close_db()


def db_reset():
    asyncio.run(reset())
