from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import getenv

db = getenv("DATABASE")
host = getenv("DATABASE_HOST")
port = int(getenv("DATABASE_PORT"))
user = getenv("DATABASE_USERNAME")
password = getenv("DATABASE_PASSWORD")
url = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{db}"
engine = create_async_engine(url,)
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)
Base = declarative_base()
