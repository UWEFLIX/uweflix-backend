from typing import Annotated

from src.crud.models import ClubsRecord
from src.crud.queries.clubs import select_club
from src.crud.queries.utils import add_object
from src.endpoints.clubs.club_members import router as club_members
from fastapi import APIRouter, Security

from src.schema.clubs import Club
from src.schema.factories.club_factories import ClubFactory
from src.schema.users import User
from src.security.security import get_current_active_user

router = APIRouter(prefix="/clubs", tags=["Clubs"])
router.include_router(club_members)


@router.post("/club-member", status_code=201, tags=["Unfinished"])
async def add_club(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=["write:club"])
        ],
        club: Club
) -> Club:
    record = ClubsRecord(
        leader=club.leader.id,
        club_name=club.club_name,
        addr_street_number=club.addr_street_number,
        addr_street_name=club.addr_street_name,
        post_code=club.post_code,
        city_id=club.city.city_id,
        landline_number=club.landline_number,
        contact_number=club.contact_number,
    )

    await add_object(record)

    record = await select_club(club.club_name)

    return ClubFactory.get_club(record)
