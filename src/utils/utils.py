import os
import string
from random import choice
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.crud.db_management import close_db
from src.crud.drop import create_new_db
from aiofiles.os import makedirs, path


ALPHABETS = list(string.ascii_uppercase)


def generate_random_string(length=6) -> str:
    letters = string.ascii_uppercase
    return ''.join(choice(letters) for _ in range(length))


async def create_assets_dir():
    _ASSETS_DIR = os.getenv('ASSETS_FOLDER')
    _FILMS_DIR = os.path.join(_ASSETS_DIR, 'images/films')

    if await path.exists(_FILMS_DIR):
        return _FILMS_DIR

    await makedirs(_FILMS_DIR)
    return _FILMS_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_assets_dir()
    # await create_new_db()
    yield
    await close_db()
