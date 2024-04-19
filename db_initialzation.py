import asyncio

from src.crud.db_management import close_db
from src.crud.drop import create_new_db


async def main():
    await create_new_db()
    await close_db()


if __name__ == '__main__':
    asyncio.run(main())
