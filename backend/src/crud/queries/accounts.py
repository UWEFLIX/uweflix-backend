from collections import defaultdict

from sqlalchemy import select, and_

from src.crud.engine import async_session
from src.crud.models import AccountsRecord, CardsRecord, UsersRecord, ClubsRecord


async def select_account(query):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.all()

            if len(rows) == 0:
                return None

            account = rows[0][0]

            if rows[0][1]:
                cards = {x[1].card_id: x[1] for x in rows}
            else:
                cards = {}

            return {
                "account": account,
                "cards": cards
            }


async def select_accounts(query):
    accounts = {

    }
    cards = defaultdict(list)
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.all()

            if len(rows) == 0:
                return None

            for row in rows:
                account = row[0]
                card = row[1]

                accounts[account.id] = {"account": account, "cards": []}
                cards[card.entity_id].append(card)

    for entity_id, cards in cards.items():
        accounts[entity_id]["cards"] = cards

    return accounts


async def select_card(card):
    query = select(
        CardsRecord
    ).where(
        CardsRecord.card_number == card
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            rows = result.scalar()

            return rows


async def check_user_card(*args):
    user_id = args[0]
    card_id = args[1]
    check_query = select(
        UsersRecord
    ).join(
        CardsRecord, CardsRecord.card_id == card_id
    ).join(
        AccountsRecord, and_(
            AccountsRecord.id == CardsRecord.account_id,
            AccountsRecord.entity_id == user_id,
            AccountsRecord.entity_type == "USER"
        )
    ).where(
        UsersRecord.user_id == user_id
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(check_query)
            return result.scalar()


async def check_club_card(*args):
    user_id = args[0]
    card_id = args[1]
    club_id = args[2]

    check_query = select(
        ClubsRecord
    ).join(
        CardsRecord, CardsRecord.card_id == card_id
    ).join(
        AccountsRecord, and_(
            AccountsRecord.id == CardsRecord.account_id,
            AccountsRecord.entity_id == club_id,
            AccountsRecord.entity_type == "CLUB"
        )
    ).where(
        ClubsRecord.id == club_id
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(check_query)
            return result.scalar()

