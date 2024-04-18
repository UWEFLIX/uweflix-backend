import time
from typing import Annotated, List
import aiofiles
from aiofiles.os import remove, path, rename
from fastapi import APIRouter, Security, UploadFile, File, HTTPException
from fastapi.params import Param
from sqlalchemy import text, delete
from starlette.responses import FileResponse
from src.crud.models import FilmImagesRecord
from src.crud.queries.films import select_film, select_images
from src.crud.queries.utils import add_objects, execute_safely
from src.schema.factories.film_factories import FilmFactory
from src.schema.users import User
from src.security.security import get_current_active_user


router = APIRouter(prefix="/images", tags=["FilmImages"])

_root_path = f'assets/images/films'


async def rename_poster(new_title: str, old_title: str) -> None:
    try:
        await rename(
            f"{_root_path}/{old_title}-poster.jpg",
            f"{_root_path}/{new_title}-poster.jpg",
        )
    except FileNotFoundError:
        pass


@router.patch("/poster", status_code=201, tags=["Unfinished"])
async def update_film_poster(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        film_title: Annotated[str, Param(title="Title of the film")],
        file: UploadFile,
) -> FileResponse:
    film_title.replace("/", "")
    film_title.replace("\\", "")
    _path = f'{_root_path}/{film_title}-poster.jpg'
    async with aiofiles.open(
            _path, 'wb'
    ) as f:
        content = await file.read()
        await f.write(content)

    return FileResponse(
        _path, status_code=201, media_type="image/jpg"
    )


@router.post("/posters", status_code=201, tags=["Unfinished"])
async def add_film_posters(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        files: List[UploadFile],
        film_title: Annotated[str, Param(title="Title of the film")],
):
    records = await select_film(film_title)

    if not records:
        raise HTTPException(
            422, detail="Film not found"
        )

    film = FilmFactory.get_full_film(records)
    batch = int(time.time())

    records = [
        FilmImagesRecord(
            film_id=film.id,
            batch=batch,
        ) for _ in range(len(files))
    ]
    await add_objects(records)

    image_records = await select_images(film.id, batch)
    images = FilmFactory.get_images(image_records)

    for index, image in enumerate(images):
        file = files[index]
        _path = f'{_root_path}/{image.filename}'

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

    _path = f'{_root_path}/{file_name}'
    _exists = await path.exists(f'{_root_path}/{file_name}')
    if _exists:
        await remove(_path)
    else:
        raise HTTPException(
            status_code=404, detail="File not found"
        )


@router.get("/image", tags=["Unfinished"])
async def get_image(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        file_name: str
) -> FileResponse:
    file_name.replace("/", "")
    file_name.replace("\\", "")

    _path = f'{_root_path}/{file_name}'
    _exists = await path.exists(f'{_root_path}/{file_name}')
    if _exists:
        return FileResponse(
            f'assets/images/films/{file_name}', media_type="image/jpg"
        )
    else:
        raise HTTPException(
            status_code=404, detail="File not found"
        )
