import asyncio
from random import randint
from typing import Annotated
from fastapi.params import Param
from sqlalchemy import update, delete, and_
from src.crud.models import ClubsRecord, AccountsRecord, ClubMembersRecords
from src.crud.queries.accounts import select_club_accounts
from src.crud.queries.clubs import select_club, select_leader_clubs, select_clubs
from src.crud.queries.utils import add_object, execute_safely, add_objects
from src.endpoints.accounts.accounts import get_initials, update_club_account_uid
from src.endpoints.clubs.club_members import router as club_members
from fastapi import APIRouter, Security, HTTPException
from src.schema.clubs import Club
from src.schema.factories.club_factories import ClubFactory
from src.schema.users import User
from src.security.security import get_current_active_user
from src.endpoints.clubs.cities import router as cities

router = APIRouter(prefix="/clubs", tags=["Clubs"])
router.include_router(club_members)
router.include_router(cities)


def update_uid_query(account_id: int, club_name: str, club_id: int):
    return update(
        AccountsRecord
    ).values(
        account_uid=f"C{account_id}#{get_initials(club_name)}"
    ).where(
        and_(
            AccountsRecord.entity_id == club_id,
            AccountsRecord.entity_type == "CLUB"
        )
    )


async def update_account_uids(club_id: int, new_name: str):
    rows = await select_club_accounts(club_id, 1, 1_000_000_000)
    queries = [
        update_uid_query(record.id, new_name, club_id) for record in rows
    ]
    tasks = [
        execute_safely(query) for query in queries
    ]
    await asyncio.gather(*tasks)


@router.post("/club", status_code=201, tags=["Unfinished"])
async def add_club(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:clubs"])
        ],
        club: Club
) -> Club:
    record = ClubsRecord(
        leader=club.leader.id,
        club_name=club.club_name,
        addr_street_number=club.addr_street_number,
        addr_street_name=club.addr_street_name,
        post_code=club.post_code,
        city_id=club.city.id,
        landline_number=club.landline_number,
        contact_number=club.contact_number,
        email=club.email
    )

    await add_object(record)

    record = await select_club(club.club_name)
    club = ClubFactory.get_full_club(record)

    accounts_record = AccountsRecord(
        account_uid=f"C{randint(0, 5000)}#{get_initials(club.club_name)}",
        name=club.club_name,
        entity_type="CLUB",
        entity_id=club.id,
        discount_rate=0,
        status="ENABLED"
    )
    club_member_record = ClubMembersRecords(
        member=club.leader.id,
        club=club.id
    )
    await add_objects([accounts_record, club_member_record])
    coro = update_club_account_uid(club.club_name, club.id, "CLUB")
    asyncio.create_task(coro)

    return club


@router.patch("/club", status_code=201, tags=["Unfinished"])
async def update_club(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        club: Club
) -> Club:

    clubs = await select_leader_clubs(current_user.id)
    try:
        old_club = clubs[club.id]
    except KeyError:
        raise HTTPException(status_code=422, detail="Club doesnt exist")

    query = update(
        ClubsRecord
    ).values(
        leader=club.leader.id,
        club_name=club.club_name,
        addr_street_number=club.addr_street_number,
        addr_street_name=club.addr_street_name,
        post_code=club.post_code,
        city_id=club.city.id,
        landline_number=club.landline_number,
        contact_number=club.contact_number,
        status=club.status
    ).where(
        ClubsRecord.id == club.id
    )

    await execute_safely(query)

    record = await select_club(club.club_name)

    if old_club.name != club.club_name:
        coro = update_account_uids(
            club.id, club.club_name,
        )
        asyncio.create_task(coro)

    return ClubFactory.get_full_club(record)


# @router.delete("/club", status_code=204, tags=["Unfinished"])
# async def delete_club(
#         current_user: Annotated[
#             User, Security(get_current_active_user, scopes=["write:clubs"])
#         ],
#         club: Club
# ) -> None:
#     query = delete(
#         ClubsRecord
#     ).where(
#         ClubsRecord.id == club.id
#     )
#
#     await execute_safely(query)
#
#     delete_accounts = delete(
#         AccountsRecord
#     ).where(
#         and_(
#             AccountsRecord.entity_type == "CLUB",
#             AccountsRecord.entity_id == club.id
#         )
#     )
#     await execute_safely(delete_accounts)


@router.get("/club", status_code=200, tags=["Unfinished"])
async def get_club(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:clubs"])
        ],
        club_name: str
):
    record = await select_club(club_name)
    return ClubFactory.get_full_club(record)


@router.get("/clubs", status_code=200, tags=["Unfinished"])
async def get_clubs(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:clubs"])
        ],
        start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
        limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)]
):
    records = await select_clubs(start, limit)

    return ClubFactory.get_half_clubs(records)
