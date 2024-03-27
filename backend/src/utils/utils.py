from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.crud.db_management import initialise_db, close_db
from src.crud.drop import create_new_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_new_db()
    pass
    yield
    await close_db()
