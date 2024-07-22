from typing import Annotated, Callable

from cryptography.fernet import InvalidToken
from fastapi import APIRouter, Security, HTTPException
from sqlalchemy import update, delete, select, or_
from src.crud.models import CardsRecord, AccountsRecord
from src.crud.queries.accounts import (
    select_card, check_user_card, check_club_card, select_half_account, select_account_from_card_id, delete_card_query,
    select_club_cards, select_user_cards
)
from src.crud.queries.clubs import select_club, select_leader_clubs
from src.crud.queries.utils import add_object, execute_safely
from src.schema.accounts import Card, CardInput
from src.schema.factories.account_factory import AccountsFactory
from src.schema.users import User
from src.security.security import get_current_active_user

router = APIRouter(prefix="/cards", tags=["Cards"])


async def validate_account(
        current_user: User, arg: int, function: Callable, error: str
) -> CardsRecord | AccountsRecord:
    record = await function(arg)

    if record is None:
        raise HTTPException(
            404, error
        )

    if record.entity_type == "CLUB":
        clubs = await select_leader_clubs(current_user.id)
        try:
            clubs[record.entity_id]
        except KeyError as e:
            raise HTTPException(
                403,
                "Not your club or club doesnt exist"
            )
    else:
        if record.entity_id != current_user.id:
            raise HTTPException(
                403,
                "Not your account"
            )

    return record


@router.post("/card", status_code=201, tags=["Unfinished"])
async def create_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card_input: CardInput
):

    card = card_input.card()

    await validate_account(
        current_user,
        card_input.account_id,
        select_half_account,
        "Account not found"
    )

    record = CardsRecord(
        account_id=card.account_id,
        card_number=card.card_number,
        holder_name=card.holder_name,
        exp_date=card.exp_date
    )

    await add_object(record)

    _card = AccountsFactory.get_card(record)
    return AccountsFactory.get_card_input(
        _card,
        card_input.user_password
    )


@router.patch("/card", status_code=201, tags=["Unfinished", "Clubs"])
async def update_club_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card_input: CardInput
):
    await validate_account(
        current_user,
        card_input.id,
        select_account_from_card_id,
        "Card not found"
    )
    card = card_input.card()
    query = update(
        CardsRecord
    ).where(
        CardsRecord.card_id == card_input.id
    ).values(
        card_number=card.card_number,
        holder_name=card.holder_name,
        exp_date=card.exp_date,
        status=card.status,
    )
    await execute_safely(query)

    record = await select_card(card_input.id)
    _card = AccountsFactory.get_card(record)

    return AccountsFactory.get_card_input(
        _card, card_input.user_password
    )


@router.delete("/card", status_code=204, tags=["Unfinished", "Users"])
async def delete_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card: Card
):
    await validate_account(
        current_user,
        card.id,
        select_account_from_card_id,
        "Card not found"
    )

    await delete_card_query(card.id)


@router.get("/card/{card_id}/{user_password/")
async def get_card(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        card_id: int, user_password: str
):
    card = await validate_account(
        current_user,
        card_id,
        select_account_from_card_id,
        "Card not found"
    )
    record = await select_card(card_id)
    _card = AccountsFactory.get_card(record)
    try:
        card_input = AccountsFactory.get_card_input(
            _card, user_password
        )
    except InvalidToken:
        raise HTTPException(422, "Incorrect password")

    return card_input


@router.get("/club/cards/{user_password/")
async def get_club_cards(
    current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
    user_password: str, club_id: int
):
    clubs = await select_leader_clubs(current_user.id)
    try:
        clubs[club_id]
    except KeyError:
        raise HTTPException(
            422,
            "Club doesnt exist or not your club"
        )

    records = await select_club_cards(club_id)
    cards = AccountsFactory.get_cards(records)

    try:
        _card = [
            AccountsFactory.get_card_input(
                card, user_password
            ) for card in cards
        ]
    except InvalidToken:
        raise HTTPException(422, "Incorrect password")

    return _card


@router.get("/user/cards/{user_password/")
async def get_user_cards(
    current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
    user_password: str,
):
    records = await select_user_cards(current_user.id)
    cards = AccountsFactory.get_cards(records)
    try:
        _card = [
            AccountsFactory.get_card_input(
                card, user_password
            ) for card in cards
        ]
    except InvalidToken:
        raise HTTPException(422, "Incorrect password")

    return _card
