from typing import Annotated, List

from fastapi import APIRouter, Security, HTTPException
from fastapi.params import Param
from sqlalchemy import update, and_, select

from src.crud.models import AccountsRecord, CardsRecord, ClubMemberRecords
from src.crud.queries.accounts import select_account, select_accounts
from src.crud.queries.clubs import select_leader_clubs
from src.crud.queries.utils import add_object, execute_safely
from src.schema.factories.account_factory import AccountsFactory
from src.security.security import get_current_active_user
from src.endpoints.accounts.cards import router as cards

router = APIRouter(prefix="/accounts", tags=["Accounts"])
router.include_router(cards)


# @router.get("/account", status_code=200, tags=["Unfinished"])
# async def get_account(
#         current_user: Annotated[
#             User, Security(get_current_active_user, scopes=[])
#         ],
#         account_id: int
# ) -> Account:
#     query = select(
#         AccountsRecord, CardsRecord
#     ).outerjoin(
#         CardsRecord, CardsRecord.account_id == AccountsRecord.id
#     ).where(
#         and_(
#             AccountsRecord.id == account_id,
#             AccountsRecord.entity_id == current_user.id
#         )
#     )
#
#     record = await select_account(query)
#
#     if not record:
#         raise HTTPException(404, "Account not found")
#
#     return AccountsFactory.get_account(record)
#
#
# @router.post("/account", status_code=201, tags=["Unfinished"])
# async def get_account(
#         current_user: Annotated[
#             User, Security(get_current_active_user, scopes=[])
#         ],
#         account: Account
# ) -> Account:
#
#     # todo finish when club is finished
#     clubs = await select_leader_clubs(current_user.id)
#
#     try:
#         clubs[account.entity_id]
#     except KeyError:
#         raise HTTPException(422, "Invalid input")
#
#     record = AccountsRecord(
#         account_uid=account.uid,
#         name=account.name,
#         entity_type="CLUB",
#         entity_id=1,
#         discount_rate=0,
#     )
#
#     await add_object(record)
#
#     query = select(
#         AccountsRecord, CardsRecord
#     ).outerjoin(
#         CardsRecord, CardsRecord.account_id == AccountsRecord.id
#     ).where(
#         and_(
#             AccountsRecord.name == account.name,
#             AccountsRecord.entity_id == current_user.id
#         )
#     )
#
#     record = await select_account(query)
#
#     if not record:
#         raise HTTPException(404, "Account not found")
#
#     return AccountsFactory.get_account(record)
#
#
# @router.patch("/accounts", status_code=201, tags=["Unfinished"])
# async def create_account(
#         current_user: Annotated[
#             User, Security(get_current_active_user, scopes=[])
#         ],
#         account: Account
# ) -> Account:
#     query = update(
#         AccountsRecord
#     ).values(
#         name=account.name,
#         uid=account.uid
#     )
#
#     if account.entity_type == "USER":
#         query.where(
#             and_(
#                 AccountsRecord.id == account.id,
#                 AccountsRecord.entity_id == current_user.id
#             )
#         )
#
#         get_query = select(
#             AccountsRecord, CardsRecord
#         ).outerjoin(
#             CardsRecord, CardsRecord.account_id == AccountsRecord.id
#         ).where(
#             and_(
#                 AccountsRecord.id == account.id,
#                 AccountsRecord.entity_id == current_user.id
#             )
#         )
#
#     else:
#         clubs = await select_leader_clubs(current_user.id)
#         try:
#             clubs[account.entity_id]
#         except KeyError:
#             raise HTTPException(422, "Invalid input")
#
#         query.where(
#             AccountsRecord.id == account.id
#         )
#
#         get_query = select(
#             AccountsRecord, CardsRecord
#         ).outerjoin(
#             CardsRecord, CardsRecord.account_id == AccountsRecord.id
#         ).where(
#             and_(
#                 AccountsRecord.id == account.id,
#                 AccountsRecord.entity_id == account.entity_id
#             )
#         )
#
#     await execute_safely(query)
#
#     record = await select_account(query)
#
#     if not record:
#         raise HTTPException(404, "Account not found")
#
#     return AccountsFactory.get_account(record)
#
#
# @router.patch("/accounts/discount", status_code=201, tags=["Unfinished"])
# async def create_account(
#         current_user: Annotated[
#             User, Security(get_current_active_user, scopes=["write:accounts"])
#         ],
#         discount: Annotated[int, Param(title="Discount amount", ge=1, le=100)],
#         account_id: Annotated[int, Param(title="Account id to update", ge=1)]
# ) -> Account:
#     query = update(
#         AccountsRecord
#     ).values(
#         discount=discount,
#     ).where(
#         AccountsRecord.account_id == account_id
#     )
#
#     await execute_safely(query)
#
#     record = await select_account(query)
#
#     if not record:
#         raise HTTPException(404, "Account not found")
#
#     return AccountsFactory.get_account(record)
#
#
# @router.get("/accounts", status_code=200, tags=["Unfinished"])
# async def get_accounts(
#         current_user: Annotated[
#             User, Security(get_current_active_user, scopes=[])
#         ],
#         start: Annotated[int, Param(title="Range starting ID to get", ge=1)],
#         limit: Annotated[int, Param(title="Amount of resources to fetch", ge=1)]
# ) -> list[Account]:
#     query = select(
#         AccountsRecord, CardsRecord
#     ).outerjoin(
#         CardsRecord, CardsRecord.account_id == AccountsRecord.id
#     ).join(
#         ClubMemberRecords, ClubMemberRecords.member == current_user.id
#     ).where(
#         and_(
#             AccountsRecord.entity_type == "CLUB",
#             AccountsRecord.id >= start
#         )
#     )
#
#     records = await select_accounts(query)
#
#     if not records:
#         raise HTTPException(404, "Account not found")
#
#     return AccountsFactory.get_accounts(records)[:limit]
