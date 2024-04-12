from typing import Annotated

from fastapi import APIRouter, Security, UploadFile, File

from src.schema.users import User
from src.security.security import get_current_active_user


router = APIRouter(prefix="/images", tags=["FilmImages"])


@router.patch("/poster", status_code=201, tags=["Unfinished"])
async def update_film_poster(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        file: UploadFile = File(...)
):
    # todo finish
    pass


@router.patch("/posters", status_code=201, tags=["Unfinished"])
async def add_film_posters(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        file: UploadFile = File(...)
):
    # todo finish
    pass


@router.patch("/posters", status_code=204, tags=["Unfinished"])
async def delete_film_posters(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:films"])
        ],
        file_name: str
):
    # todo finish
    pass


@router.get("/image", tags=["Unfinished"])
async def get_image(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
):
    # todo finish
    pass
