import asyncio
from typing import Annotated
from fastapi import APIRouter, Security, HTTPException
from pydantic import EmailStr
from sqlalchemy import update, delete, select, and_, or_
from src.crud.models import UsersRecord, CardsRecord, AccountsRecord, ClubsRecord
from src.crud.queries.user import select_user_by_email
from src.crud.queries.utils import execute_safely, scalar_selection
from src.schema.users import (
    User, PasswordChange, ResetRequest, PasswordResetConfirmation
)
from src.security.security import (
    get_current_active_user, verify_password, get_password_hash, EMAILS, otp
)

router = APIRouter(prefix="/passwords", tags=["Passwords"])


@router.post("/change", status_code=204, tags=["Unfinished"])
async def change_password(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ],
        form: PasswordChange
):
    if not verify_password(form.old_password, current_user.password):
        raise HTTPException(
            422, "Old password doesnt match with current password"
        )

    new_password = get_password_hash(form.new_password)

    query = update(
        UsersRecord
    ).values(
        password=new_password
    ).where(
        UsersRecord.user_id == current_user.id
    )

    await execute_safely(query)


@router.post("/reset/request", status_code=204, tags=['Unfinished'])
async def reset_request(email: EmailStr):
    record = await select_user_by_email(email)

    if not record:
        raise HTTPException(404, "User not found")

    users_record: UsersRecord = record["user"]

    obj = ResetRequest(
        otp=otp.generate(
            users_record.password + users_record.email
        ),
        email=email
    )

    await EMAILS.password_reset_email(obj)
    return


@router.post("/reset/reset", status_code=204, tags=['Unfinished'])
async def password_reset_confirmation(form: PasswordResetConfirmation):
    record = await select_user_by_email(form.email)

    if not record:
        raise HTTPException(404, "User not found")

    users_record: UsersRecord = record["user"]

    identifier = users_record.password + users_record.email
    if not otp.verify(
            form.otp, identifier
    ):
        raise HTTPException(422, "Invalid otp")

    new_password = get_password_hash(form.new_password)

    query = update(
        UsersRecord
    ).values(
        password=new_password
    ).where(
        UsersRecord.email == users_record.email
    )

    personal_account_query = select(
        AccountsRecord
    ).where(
        and_(
            AccountsRecord.entity_id == users_record.user_id,
            AccountsRecord.entity_type == "USER"
        )
    )
    club_account_query = select(
        AccountsRecord
    ).join(
        ClubsRecord, AccountsRecord.entity_id == ClubsRecord.id
    ).where(
        and_(
            ClubsRecord.leader == users_record.user_id,
            AccountsRecord.entity_type == "CLUB"
        )
    )

    personal_account_record, club_account_record = \
        await asyncio.gather(
            scalar_selection(personal_account_query),
            scalar_selection(club_account_query)
        )
    accounts = [personal_account_record.id]
    if club_account_record:
        accounts.append(club_account_record.id)

    card_delete_query = delete(
        CardsRecord
    ).where(
        or_(*[
            CardsRecord.account_id == x for x in accounts
        ])
    )

    await asyncio.gather(
        execute_safely(query),
        execute_safely(card_delete_query)
    )
