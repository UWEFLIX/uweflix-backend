import asyncio
from random import randint
from typing import Annotated, List
from fastapi.params import Param
from sqlalchemy import update, delete, and_, select, or_
from sqlalchemy.orm import aliased

from src.crud.models import ClubsRecord, AccountsRecord, ClubMembersRecords, CitiesRecord, UsersRecord
from src.crud.queries.accounts import select_club_accounts
from src.crud.queries.clubs import select_club, select_leader_clubs, select_clubs, select_club_members, \
    select_club_by_id
from src.crud.queries.utils import add_object, execute_safely, add_objects, scalar_selection, all_selection
from src.endpoints.accounts.accounts import get_initials, update_club_account_uid
from src.endpoints.clubs.club_members import router as club_members
from fastapi import APIRouter, Security, HTTPException
from src.schema.clubs import Club
from src.schema.factories.account_factory import AccountsFactory
from src.schema.factories.club_factories import ClubFactory
from src.schema.factories.user_factory import UserFactory
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


async def _add_members(
        members: List[User] | None, club_id: int, leader_id: int
) -> None:
    if not members:
        return

    records: List[ClubMembersRecords] = await select_club_members(club_id)

    members_in_record = set(record.member for record in records)
    members_in_request = set(member.id for member in members)

    members_to_delete = members_in_record - members_in_request
    members_to_add = members_in_request - members_in_record

    if leader_id in members_to_delete:
        raise HTTPException(
            403,
            "Wrong endpoint to delete leader"
        )

    tasks = [
        execute_safely(
            delete(
                ClubMembersRecords
            ).where(
                and_(
                    ClubMembersRecords.club == club_id,
                    ClubMembersRecords.member == member_id
                )
            )
        ) for member_id in members_to_delete
    ]
    # delete_query = delete(
    #     ClubMembersRecords
    # ).where(
    #     [
    #         and_(
    #             ClubMembersRecords.club == club_id,
    #             ClubMembersRecords.member == member_id
    #         )
    #     ] for member_id in members_to_delete
    # )

    add_query = [
        ClubMembersRecords(
            member=member,
            club=club_id
        ) for member in members_to_add
    ]

    if len(members_to_add):
        tasks.append(add_objects(add_query))

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
        account_uid=f"C{club.id}#{get_initials(club.club_name)}",
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
    records = [accounts_record, club_member_record]
    records.extend([
        ClubMembersRecords(
            member=member.id,
            club=club.id
        ) for member in club.members
    ])
    await add_objects(records)

    return club


@router.patch("/admin/club", status_code=201, tags=["Unfinished"])
async def admin_update_club(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:clubs"])
        ],
        club: Club
) -> Club:
    query = update(
        ClubsRecord
    ).values(
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

    uid_update = update(
        AccountsRecord
    ).values(
        account_uid=f"C{club.id}#{get_initials(club.club_name)}"
    ).where(
        and_(
            AccountsRecord.entity_id == club.id,
            AccountsRecord.entity_type == "CLUB"
        )
    )

    tasks = [
        _add_members(club.members, club.id, club.leader.id),
        execute_safely(query),
        execute_safely(uid_update)
    ]

    await asyncio.gather(*tasks)

    record = await select_club(club.club_name)
    return ClubFactory.get_full_club(record)


@router.patch("/club", status_code=201, tags=["Unfinished"])
async def update_club(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        club: Club
) -> Club:

    clubs = await select_leader_clubs(current_user.id)
    try:
        old_club = clubs[club.id][0]
    except KeyError:
        raise HTTPException(status_code=422, detail="Club doesnt exist")

    query = update(
        ClubsRecord
    ).values(
        club_name=club.club_name,
        addr_street_number=club.addr_street_number,
        addr_street_name=club.addr_street_name,
        post_code=club.post_code,
        city_id=club.city.id,
        landline_number=club.landline_number,
        contact_number=club.contact_number,
        # status=club.status
        email=club.email,
    ).where(
        ClubsRecord.id == club.id
    )

    tasks = [
        _add_members(club.members, club.id, club.leader.id),
        execute_safely(query)
    ]
    await asyncio.gather(*tasks)

    record = await select_club(club.club_name)

    if old_club.club_name != club.club_name:
        uid_update = update(
            AccountsRecord
        ).values(
            account_uid=f"C{club.id}#{get_initials(club.club_name)}"
        ).where(
            and_(
                AccountsRecord.entity_id == club.id,
                AccountsRecord.entity_type == "CLUB"
            )
        )
        asyncio.create_task(execute_safely(uid_update))

    return ClubFactory.get_full_club(record)


@router.get("/club", status_code=200, tags=["Unfinished"])
async def get_club(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:clubs"])
        ],
        club_name: str
):
    record = await select_club(club_name)

    if record is None:
        raise HTTPException(
            404, "Club not found"
        )

    return ClubFactory.get_full_club(record)


@router.get("/club/id/{club_id}", status_code=200, tags=["Unfinished"])
async def get_club(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:clubs"])
        ],
        club_id: int
):
    record = await select_club_by_id(club_id)

    if record is None:
        raise HTTPException(
            404, "Club not found"
        )

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


@router.get("/club/me")
async def get_my_club(
    current_user: Annotated[
            User, Security(get_current_active_user, scopes=["read:clubs"])
        ],
):
    query = select(
        ClubsRecord, CitiesRecord, UsersRecord, AccountsRecord
    ).join(
        ClubMembersRecords, ClubMembersRecords.club == ClubsRecord.id
    ).join(
        CitiesRecord, CitiesRecord.city_id == ClubsRecord.city_id
    ).join(
        UsersRecord, UsersRecord.user_id == ClubsRecord.leader
    ).join(
        AccountsRecord, and_(
            AccountsRecord.entity_id == ClubsRecord.id,
            AccountsRecord.entity_type == "CLUB"
        )
    ).where(
        ClubMembersRecords.member == current_user.id
    )

    records = await all_selection(query)

    if len(records) == 0:
        raise HTTPException(404, "Club not found")

    leader = UserFactory.create_half_user(records[0][2])
    account = AccountsFactory.get_half_account(records[0][3])
    club = ClubFactory.get_half_club(records[0])
    club.leader = leader
    club.account = account
    return club
