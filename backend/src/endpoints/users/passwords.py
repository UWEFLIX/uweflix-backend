from typing import Annotated

from fastapi import APIRouter, Security, HTTPException
from pydantic import EmailStr
from sqlalchemy import update

from src.crud.models import UsersRecord
from src.crud.queries.user import select_user_by_email
from src.crud.queries.utils import execute_safely
from src.schema.users import User, PasswordChange, ResetRequest, PasswordResetConfirmation
from src.security.security import get_current_active_user, verify_password, get_password_hash, EMAILS, otp

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

    await execute_safely(query)

