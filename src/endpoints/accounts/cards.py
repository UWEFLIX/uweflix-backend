from typing import Annotated, Callable
from fastapi import APIRouter, Security, HTTPException
from sqlalchemy import update, delete
from src.crud.models import CardsRecord
from src.crud.queries.accounts import (
    select_card, check_user_card, check_club_card
)
from src.crud.queries.utils import add_object, execute_safely
from src.schema.accounts import Card
from src.schema.factories.account_factory import AccountsFactory
from src.schema.users import User
from src.security.security import get_current_active_user

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.post("/card", status_code=201, tags=["Unfinished"])
async def create_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card: Card
):

    card.validate_card()
    card.encrypt()

    record = CardsRecord(
        account_id=card.account_id,
        card_number=card.card_number,
        holder_name=card.holder_name,
        exp_date=card.exp_date
    )

    await add_object(record)

    record = await select_card(card.card_number)
    _card = AccountsFactory.get_card(record)
    _card.decrypt()
    return _card


async def _update_card(card: Card, current_user: User, check: Callable):
    card.validate_card()
    card.encrypt()

    record = await check([current_user.id, card.id])
    if not record:
        raise HTTPException(status_code=422, detail="Invalid details")

    query = update(
        CardsRecord
    ).values(
        card_number=card.card_number,
        holder_name=card.holder_name,
        exp_date=card.exp_date
    ).where(
        CardsRecord.card_id == card.id
    )

    await execute_safely(query)

    record = await select_card(card.card_number)
    _card = AccountsFactory.get_card(record)
    _card.decrypt()
    return _card


async def _delete_card(card: Card, current_user: User, check: Callable):
    record = await check(current_user.id, card.id)
    if not record:
        raise HTTPException(status_code=422, detail="Invalid details")

    query = delete(
        CardsRecord
    ).where(
        CardsRecord.card_id == card.id
    )
    await execute_safely(query)


@router.patch("/user/card", status_code=201, tags=["Unfinished", "Users"])
async def update_user_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card: Card
):
    return await _update_card(card, current_user, check_user_card)


@router.patch("/club/card", status_code=201, tags=["Unfinished", "Clubs"])
async def update_club_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card: Card
):
    return await _update_card(card, current_user, check_club_card)


@router.delete("/club/card", status_code=204, tags=["Unfinished", "Clubs"])
async def delete_club_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card: Card
):
    await _delete_card(card, current_user, check_club_card)


@router.delete("/user/card", status_code=204, tags=["Unfinished", "Users"])
async def delete_user_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card: Card
):
    await _delete_card(card, current_user, check_user_card)
