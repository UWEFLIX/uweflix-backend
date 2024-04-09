from typing import Annotated

from fastapi import APIRouter, Security

from src.crud.models import CardsRecord
from src.crud.queries.accounts import select_card
from src.crud.queries.utils import add_object
from src.schema.factories.account_factory import AccountsFactory
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
    record = CardsRecord(
        account_id=card.account_id,
        card_number=card.card_number,
        holder_name=card.holder_name,
        exp_date=card.exp_date,
        status=card.status
    )

    await add_object(record)

    record = await select_card(card.card_number)
    return AccountsFactory.get_account(record)


@router.patch("/card", status_code=201, tags=["Unfinished"])
async def update_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card: Card
):
    record = CardsRecord(
        account_id=card.account_id,
        card_number=card.card_number,
        holder_name=card.holder_name,
        exp_date=card.exp_date,
        status=card.status
    )

    await add_object(record)

    record = await select_card(card.card_number)
    return AccountsFactory.get_account(record)
