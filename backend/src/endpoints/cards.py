from typing import Annotated

from fastapi import APIRouter, Security

from src.schema.users import User, Card
from src.security.security import get_current_active_user

router = APIRouter(prefix="/cards")


@router.post("/card", status_code=201, tags=["Unfinished"])
async def create_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card: Card
):

