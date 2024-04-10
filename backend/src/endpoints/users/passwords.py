from fastapi import APIRouter


router = APIRouter(prefix="/passwords", tags=["Passwords"])


async def change_password():
    pass
