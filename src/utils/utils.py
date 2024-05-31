import asyncio
import json
import os
import string
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from random import choice
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.crud.db_management import close_db
from src.crud.drop import create_new_db
from aiofiles.os import makedirs, path


ALPHABETS = list(string.ascii_uppercase)


async def save_openai():
    import urllib3
    await asyncio.sleep(5)

    http = urllib3.PoolManager()

    port = os.getenv("PORT")

    # Specify the URL
    url = f"http://127.0.0.1:{port}/openapi.json"
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor() as executor:
        response = await loop.run_in_executor(
            executor,
            http.request,
            'GET', url
        )

    content = json.loads(response.data.decode('utf-8'))
    with open("docs/openapi.json", "w") as f:
        json.dump(content, f, indent=4)


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


def str_to_iso_format(_string: str):
    return datetime.fromisoformat(
        _string.replace('Z', '+00:00')
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_assets_dir()

    is_dev = int(os.getenv('DEV'))
    print(is_dev)
    if is_dev:
        asyncio.create_task(save_openai())

    yield
    await close_db()
