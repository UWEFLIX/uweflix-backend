import asyncio
from dotenv import load_dotenv
from src.crud.db_management import close_db
from src.crud.drop import create_new_db
from src.crud.engine import db, host, port, user, password

load_dotenv()


async def main():
    print(f"db: {db}")
    print(f"host: {host}")
    print(f"port: {port}")
    print(f"user: {user}")
    print(f"password: {password}")

    await create_new_db()
    await close_db()


if __name__ == '__main__':
    asyncio.run(main())
