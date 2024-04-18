from typing import Annotated, List
from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from sqlalchemy import update, and_, select
from src.crud.models import AccountsRecord, CardsRecord
from src.crud.queries.accounts import (
    select_account, select_half_account, select_half_accounts,
    select_last_entered_account, select_full_account, select_club_accounts
)
from src.crud.queries.clubs import select_leader_clubs
from src.crud.queries.utils import add_object, execute_safely
from src.schema.accounts import Account
from src.schema.factories.account_factory import AccountsFactory
from src.schema.users import User
from src.security.security import get_current_active_user
from src.endpoints.accounts.cards import router as cards

router = APIRouter(prefix="/accounts", tags=["Accounts"])
router.include_router(cards)


# todo test user and club get endpoints


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


@router.patch("/account", status_code=201, tags=["Unfinished"])
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
        AccountsRecord.id == account_id
    )
    await execute_safely(query)


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


@router.post("/club/account", status_code=201, tags=["Unfinished", "Clubs"])
async def create_account(
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

    record = AccountsRecord(
        account_uid=account.uid,
        name=account.name,
        entity_type="CLUB",
        entity_id=account.entity_id,
        discount_rate=0,
    )

    await add_object(record)

    new_record = select_last_entered_account(
        account.name, current_user.id
    )
    return AccountsFactory.get_half_account(new_record)


async def _update_account(
        account: Account, entity_id: int, entity_type: str
) -> Account:
    query = update(
        AccountsRecord
    ).values(
        name=account.name,
        uid=account.uid,
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
        account_id: int, entity_id: int, entity_type: str
) -> Account:
    query = select(
        AccountsRecord, CardsRecord
    ).outerjoin(
        CardsRecord.account_id == AccountsRecord.id
    ).where(
        and_(
            AccountsRecord.id == account_id,
            AccountsRecord.entity_id == entity_id,
            AccountsRecord.entity_type == entity_type
        )
    )

    records = await select_full_account(query)
    return AccountsFactory.get_account(records)


@router.get("/user/account", status_code=201, tags=["Unfinished", "Users"])
async def get_user_account(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ]
) -> Account:
    query = select(
        AccountsRecord, CardsRecord
    ).join(
        CardsRecord.account_id == AccountsRecord.id
    ).where(
        and_(
            AccountsRecord.entity_id == current_user.id,
            AccountsRecord.entity_type == "USER"
        )
    )
    records = await select_full_account(query)
    return AccountsFactory.get_account(records)


@router.get("/club/account", status_code=201, tags=["Unfinished", "Clubs"])
async def get_club_account(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        account_id: int, club_id: int
) -> Account:
    clubs = await select_leader_clubs(current_user.id)

    try:
        clubs[club_id]
    except KeyError:
        raise HTTPException(422, "Invalid input")

    return await _select_account(account_id, club_id, "CLUB")


@router.get("/club/accounts", status_code=201, tags=["Unfinished", "Clubs"])
async def get_club_accounts(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        club_id: Annotated[int, Param(title="Club ID off accounts", ge=1)],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)]
) -> List[Account]:
    clubs = await select_leader_clubs(current_user.id)

    try:
        clubs[club_id]
    except KeyError:
        raise HTTPException(
            422, "You are not the leader of the club"
        )

    records = await select_club_accounts(club_id, start, limit)
    return AccountsFactory.get_half_accounts(records)


# todo top up
