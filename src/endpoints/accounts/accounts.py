import random
import string
from typing import Annotated, List
from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from sqlalchemy import update, and_, select
from src.crud.models import AccountsRecord, CardsRecord
from src.crud.queries.accounts import (
    select_account, select_half_account, select_half_accounts,
    select_last_entered_account, select_full_account, select_club_accounts
)
from src.crud.queries.clubs import select_leader_clubs, select_club_with_accounts, select_club_by_id
from src.crud.queries.utils import add_object, execute_safely, scalar_selection
from src.schema.accounts import Account, TopUp
from src.schema.clubs import Club
from src.schema.factories.account_factory import AccountsFactory
from src.schema.factories.club_factories import ClubFactory
from src.schema.users import User
from src.security.security import get_current_active_user
from src.endpoints.accounts.cards import router as cards

router = APIRouter(prefix="/accounts", tags=["Accounts"])
router.include_router(cards)

# todo fix account uid


def get_initials(name: str):
    words = name.split(" ")
    return ". ".join([word[0].upper() for word in words])


async def update_club_account_uid(
        name: str, entity_id: int, entity_type: str
) -> Account:
    query = select(
        AccountsRecord
    ).where(
        and_(
            AccountsRecord.entity_id == entity_id,
            AccountsRecord.entity_type == entity_type
        )
    )
    # name = Hello, entity_id = 28, entity_type = USER
    new_record = await scalar_selection(query)

    if new_record is None:
        return

    if entity_type == "USER":
        char = "U"
    else:
        char = "C"

    if new_record is None:
        pass

    _account = AccountsFactory.get_half_account(new_record)
    uid = f"{char}{_account.id}#{get_initials(name)}"
    _account.uid = uid

    _query = update(
        AccountsRecord
    ).values(
        account_uid=uid
    ).where(AccountsRecord.id == _account.id)
    await execute_safely(_query)

    return _account


@router.get("/account", status_code=200, tags=["Unfinished"])
async def get_account(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:accounts"])
        ],
        account_id: int
) -> Account:
    record = await select_half_account(account_id)

    if not record:
        raise HTTPException(404, "Account not found")

    return AccountsFactory.get_half_account(record)


@router.patch("/club/account", status_code=201, tags=["Unfinished"])
async def update_account_discount(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:accounts"])
        ],
        account_id: Annotated[
            int, Param(title="Account id to update", ge=0)
        ],
        discount: Annotated[
            int, Param(title="New discount amount of account", ge=0, le=100)
        ],
):
    query = update(
        AccountsRecord
    ).values(
        discount_rate=discount
    ).where(
        and_(
            AccountsRecord.id == account_id,
            AccountsRecord.entity_type == "CLUB"
        )
    )
    await execute_safely(query)
    # todo finish


@router.get("/accounts", status_code=200, tags=["Unfinished"])
async def get_accounts(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:accounts"])
        ],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)]
) -> List[Account]:
    record = await select_half_accounts(start, limit)
    return AccountsFactory.get_half_accounts(record)


@router.post(
    "/club/account",
    status_code=201, tags=["Unfinished", "Clubs"]
)
async def create_account(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[
                "write:accounts"
            ])
        ],
        account: Account
) -> Account:
    record = await select_club_by_id(account.entity_id)
    club = record["club"]
    if club is None:
        raise HTTPException(
            404, "Club not found"
        )

    record = AccountsRecord(
        account_uid=''.join(
            random.choices(
                string.ascii_letters + string.digits, k=4
            )
        ),
        name=account.name,
        entity_type="CLUB",
        entity_id=account.entity_id,
        discount_rate=0,
        status="ENABLED"
    )

    await add_object(record)

    return await update_club_account_uid(
        club.club_name, account.entity_id, "CLUB"
    )


async def _update_account(
        account: Account, entity_id: int, entity_type: str
) -> Account:
    uid = f"{account.id}#{get_initials(account.name)}"
    query = update(
        AccountsRecord
    ).values(
        name=account.name,
        account_uid=uid,
        status=account.status
    ).where(
        and_(
            AccountsRecord.id == account.id,
            AccountsRecord.entity_id == entity_id,
            AccountsRecord.entity_type == entity_type
        )
    )

    await execute_safely(query)

    select_query = select(
        AccountsRecord
    ).where(
        and_(
            AccountsRecord.id == account.id,
            AccountsRecord.entity_id == entity_id,
            AccountsRecord.entity_type == entity_type
        )
    )

    record = await select_account(select_query)

    if not record:
        raise HTTPException(404, "Account not found")

    return AccountsFactory.get_half_account(record)


@router.patch("/club/account", status_code=201, tags=["Unfinished", "Clubs"])
async def update_club_account(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        account: Account
) -> Account:
    clubs = await select_leader_clubs(current_user.id)

    try:
        clubs[account.entity_id]
    except KeyError:
        raise HTTPException(422, "Invalid input")
    return await _update_account(account, account.entity_id, "CLUB")


@router.patch("/user/account", status_code=201, tags=["Unfinished", "Users"])
async def update_user_account(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        account: Account
) -> Account:
    return await _update_account(account, current_user.id, "USER")


async def _select_account(
        account_id: int, entity_type: str
) -> Account:
    query = select(
        AccountsRecord, CardsRecord
    ).outerjoin(
        CardsRecord, CardsRecord.account_id == AccountsRecord.id
    ).where(
        and_(
            AccountsRecord.id == account_id,
            AccountsRecord.entity_type == entity_type
        )
    )

    records = await select_full_account(query)
    return AccountsFactory.get_account(records)


@router.get("/account/me", status_code=201, tags=["Unfinished", "Users"])
async def get_user_account(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ]
) -> Account:
    query = select(
        AccountsRecord
    ).where(
        and_(
            AccountsRecord.entity_id == current_user.id,
            AccountsRecord.entity_type == "USER"
        )
    )
    records = await scalar_selection(query)

    if records is None:
        raise HTTPException(
            404, "Account Not Found"
        )
    return AccountsFactory.get_half_account(records)


@router.get("/user/account/{user_id}", status_code=201, tags=["Unfinished", "Users"])
async def get_user_account(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:accounts"])
        ],
        user_id: int
) -> Account:
    query = select(
        AccountsRecord
    ).where(
        and_(
            AccountsRecord.entity_id == user_id,
            AccountsRecord.entity_type == "USER"
        )
    )
    records = await scalar_selection(query)

    if records is None:
        raise HTTPException(
            404, "Account Not Found"
        )
    return AccountsFactory.get_half_account(records)


@router.get("/club/account/{account_id}/", status_code=201, tags=["Unfinished", "Clubs"])
async def get_club_account(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        account_id: int
) -> Account:
    # clubs = await select_leader_clubs(current_user.id)
    #
    # try:
    #     clubs[club_id]
    # except KeyError:
    #     raise HTTPException(422, "Invalid input")

    return await _select_account(account_id, "CLUB")


@router.get(
    "/club/account/id/{account_id}",
    status_code=201, tags=["Unfinished", "Clubs"]
)
async def get_account_with_club(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        account_id: int
) -> Club:
    records = await select_club_with_accounts(account_id)

    if records is None:
        raise HTTPException(404, "Account not found")

    account = AccountsFactory.get_account(records)
    club = ClubFactory.get_full_club(records)
    club.account = account

    return club


@router.get("/club/accounts", status_code=201, tags=["Unfinished", "Clubs"])
async def get_club_accounts(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        club_id: Annotated[int, Param(title="Club ID off accounts", ge=1)],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)]
) -> List[Account]:
    records = await select_club_accounts(club_id, start, limit)
    return AccountsFactory.get_half_accounts(records)


@router.post(
    "/account/top-up", status_code=201, tags=["Unfinished", "Clubs"]
)
async def club_top_up(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        top_up: TopUp
):
    query = select(
        CardsRecord
    ).where(
        CardsRecord.card_id == top_up.card_id
    )
    record = await scalar_selection(query)
    card = AccountsFactory.get_card(record)
    card_input = AccountsFactory.get_card_input(card, top_up.user_password)

    update_query = update(
        AccountsRecord
    ).values(
        balance=AccountsRecord.balance + top_up.amount
    ).where(
        AccountsRecord.id == top_up.account_id
    )
    await execute_safely(update_query)

    record = await select_half_account(top_up.account_id)
    if not record:
        raise HTTPException(404, "Account not found")

    return AccountsFactory.get_half_account(record)
