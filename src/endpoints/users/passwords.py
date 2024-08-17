import asyncio
from typing import Annotated
from fastapi import APIRouter, Security, HTTPException
from pydantic import EmailStr
from sqlalchemy import update, delete, select, and_, or_
from src.crud.models import UsersRecord, CardsRecord, AccountsRecord, ClubsRecord
from src.crud.queries.user import select_user_by_email
from src.crud.queries.utils import execute_safely, scalar_selection, scalars_selection
from src.schema.factories.account_factory import AccountsFactory
from src.schema.users import (
    User, PasswordChange, ResetRequest, PasswordResetConfirmation
)
from src.security.security import (
    get_current_active_user, verify_password, get_password_hash, EMAILS, otp
)

router = APIRouter(prefix="/passwords", tags=["Passwords"])


async def reencrypt_cards(
        user_id: int,
        old_password: str,
        new_password: str
) -> None:
    personal_account_query = select(
        AccountsRecord
    ).where(
        and_(
            AccountsRecord.entity_id == user_id,
            AccountsRecord.entity_type == "USER"
        )
    )
    club_account_query = select(
        AccountsRecord
    ).join(
        ClubsRecord, AccountsRecord.entity_id == ClubsRecord.id
    ).where(
        and_(
            ClubsRecord.leader == user_id,
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

    select_cards_query = select(
        CardsRecord
    ).where(
        or_(
            *[
                CardsRecord.account_id == x for x in accounts
            ]
        )
    )
    card_records = await scalars_selection(select_cards_query)
    if not card_records:
        return

    encrypted_cards = [
        AccountsFactory.get_card(
            record
        ) for record in card_records
    ]
    # decrypted_cards = [
    #     AccountsFactory.get_card_input(
    #         _card,
    #         old_password
    #     ) for _card in encrypted_cards
    # ]
    tasks = []
    for encrypted_card in encrypted_cards:
        card = AccountsFactory.get_card_input(encrypted_card, old_password)
        card.user_password = new_password

        re_encrypted_card = card.card()
        query = update(
            CardsRecord
        ).values(
            card_number=re_encrypted_card.card_number,
            holder_name=re_encrypted_card.holder_name,
            exp_date=re_encrypted_card.exp_date,
        ).where(
            CardsRecord.card_id == card.id
        )
        tasks.append(execute_safely(query))

    await asyncio.gather(
        *tasks
    )


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

    asyncio.create_task(
        reencrypt_cards(current_user.id, form.old_password, form.new_password)
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
