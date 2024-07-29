import asyncio
import os
import time
from typing import Annotated, List
import aiofiles
from aiofiles.os import remove, path, rename
from fastapi import APIRouter, Security, UploadFile, File, HTTPException
from fastapi.params import Param, Path
from sqlalchemy import text, delete
from starlette.responses import FileResponse
from src.crud.models import FilmImagesRecord
from src.crud.queries.films import select_film, select_images, select_film_by_id, select_poster_images
from src.crud.queries.utils import add_objects, execute_safely
from src.schema.factories.film_factories import FilmFactory
from src.schema.users import User
from src.security.security import get_current_active_user


router = APIRouter(prefix="/images", tags=["FilmImages"])

_ASSETS_DIR = os.getenv('ASSETS_FOLDER')
_FILMS_DIR = os.path.join(_ASSETS_DIR, 'images/films')


async def rename_poster(new_title: str, old_title: str) -> None:
    try:
        await rename(
            f"{_FILMS_DIR}/{old_title}-poster.jpg",
            f"{_FILMS_DIR}/{new_title}-poster.jpg",
        )
    except FileNotFoundError:
        pass


@router.patch("/poster/{film_id}", status_code=201, tags=["Unfinished"])
async def update_film_poster(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        film_id: int,
        file: UploadFile,
) -> FileResponse:
    film = await select_film_by_id(film_id)

    if film is None:
        raise HTTPException(
            404, "Film not found"
        )

    _path = f'{_FILMS_DIR}/{film_id}-poster.jpg'
    async with aiofiles.open(
            _path, 'wb'
    ) as f:
        content = await file.read()
        await f.write(content)

    return FileResponse(
        _path, status_code=201, media_type="image/jpg"
    )


async def _delete_image(filename: str) -> None:
    try:
        await remove(f'{_FILMS_DIR}/{filename}')
    except FileNotFoundError as e:
        print("File Not Found " + str(e))


@router.patch("/posters/{film_id}", status_code=201, tags=["Unfinished"])
async def add_film_posters(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        files: List[UploadFile],
        film_id: Annotated[int, Path(title="ID of the film")],
):
    new_records = await select_film_by_id(film_id)

    if not new_records:
        raise HTTPException(
            422, detail="Film not found"
        )

    film = FilmFactory.get_full_film(new_records)
    batch = int(time.time())

    existing_records = await select_poster_images(film_id)
    existing_images = FilmFactory.get_images(existing_records)
    query = execute_safely(
        delete(
            FilmImagesRecord
        ).where(
            FilmImagesRecord.film_id == film_id
        )
    )
    tasks = [
        _delete_image(image.filename) for image in
        existing_images
    ]
    tasks.append(query)

    await asyncio.gather(
        *tasks
    )

    new_records = [
        FilmImagesRecord(
            film_id=film.id,
            batch=batch,
        ) for _ in range(len(files))
    ]
    await add_objects(new_records)

    image_records = await select_images(film.id, batch)
    images = FilmFactory.get_images(image_records)

    for index, image in enumerate(images):
        file = files[index]
        _path = f'{_FILMS_DIR}/{image.filename}'

        async with aiofiles.open(
                _path, 'wb'
        ) as f:
            content = await file.read()
            await f.write(content)

    return images


@router.delete("/posters", status_code=204, tags=["Unfinished"])
async def delete_film_posters(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        file_name: str
):
    file_name.replace("/", "")
    file_name.replace("\\", "")

    try:
        _file_name = file_name.split(".")[0]
    except IndexError:
        raise HTTPException(status_code=422, detail="Invalid filename")

    query = delete(
        FilmImagesRecord
    ).where(FilmImagesRecord.filename == _file_name)
    await execute_safely(query)

    _path = f'{_FILMS_DIR}/{file_name}'
    _exists = await path.exists(f'{_FILMS_DIR}/{file_name}')
    if _exists:
        await remove(_path)
    else:
        raise HTTPException(
            status_code=404, detail="File not found"
        )


@router.get("/image/{file_name}", tags=["Unfinished", "Public"])
async def get_image(
        file_name: str
) -> FileResponse:
    file_name.replace("/", "")
    file_name.replace("\\", "")

    _path = f'{_FILMS_DIR}/{file_name}'
    _exists = await path.exists(_path)
    if _exists:
        return FileResponse(
            f'{_FILMS_DIR}/{file_name}', media_type="image/jpg"
        )
    else:
        raise HTTPException(
            status_code=404, detail="File not found"
        )
