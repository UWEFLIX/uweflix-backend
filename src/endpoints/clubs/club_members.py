from typing import Annotated
from fastapi import APIRouter, Security, HTTPException
from sqlalchemy import and_, delete, select
from src.crud.models import ClubMembersRecords, UsersRecord
from src.crud.queries.clubs import select_leader_clubs
from src.crud.queries.utils import add_object, execute_safely, scalars_selection
from src.schema.factories.user_factory import UserFactory
from src.schema.users import User
from src.security.security import get_current_active_user

router = APIRouter(prefix="/clubs", )


@router.post("/member", status_code=201, tags=["Unfinished"])
async def add_club_member(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        user_id: int, club_id: int
) -> dict:
    clubs = await select_leader_clubs(current_user.id)
    try:
        club = clubs[club_id]
    except KeyError:
        raise HTTPException(status_code=422, detail="Club doesnt exist")

    if club.status != "ENABLED":
        raise HTTPException(
            422, "Club is not enabled"
        )

    record = ClubMembersRecords(
        member=user_id,
        club=club_id
    )

    await add_object(record)

    return {"details": "Success"}


@router.delete("/member", status_code=204, tags=["Unfinished"])
async def remove_club_member(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        user_id: int, club_id: int
) -> None:
    clubs = await select_leader_clubs(current_user.id)
    try:
        clubs[club_id]
    except KeyError:
        raise HTTPException(status_code=422, detail="Club doesnt exist")

    query = delete(
        ClubMembersRecords
    ).where(
        and_(
            ClubMembersRecords.member == user_id,
            ClubMembersRecords.club == club_id,
        )
    )

    await execute_safely(query)

    # return {"details": "Success"}


@router.get("/members/{club_id}/")
async def get_members(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        club_id: int
):
    query = select(
        UsersRecord
    ).join(
        ClubMembersRecords,
        ClubMembersRecords.member == UsersRecord.user_id
    ).where(
        ClubMembersRecords.club == club_id
    )
    records = await scalars_selection(query)
    return [UserFactory.create_half_user(record) for record in records]
