from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.crud.db_management import close_db
from src.crud.drop import create_new_db
from src.crud.queries.utils import add_object


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_new_db()
    pass
    yield
    await close_db()
