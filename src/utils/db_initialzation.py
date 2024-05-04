import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.crud.db_management import close_db
from src.crud.drop import create_new_db
from src.crud.engine import db, host, port, user, password


async def _main():
    await create_new_db()
    await close_db()


def main():
    asyncio.run(_main())
