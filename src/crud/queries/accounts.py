from collections import defaultdict

from sqlalchemy import select, and_, ScalarResult, asc

from src.crud.engine import async_session
from src.crud.models import AccountsRecord, CardsRecord, UsersRecord, ClubsRecord


async def select_account(query):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalar()

            # if len(rows) == 0:
            #     return None
            #
            # account = rows[0][0]
            #
            # if rows[0][1]:
            #     cards = {x[1].card_id: x[1] for x in rows}
            # else:
            #     cards = {}
            #
            # return {
            #     "account": account,
            #     "cards": cards
            # }


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


async def check_user_card(user_id, card_id):
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


async def check_club_card(user_id, card_id):

    check_query = select(
        ClubsRecord
    ).join(
        CardsRecord, CardsRecord.card_id == card_id
    ).join(
        UsersRecord, ClubsRecord.leader == UsersRecord.id
    ).join(
        AccountsRecord, and_(
            AccountsRecord.id == CardsRecord.account_id,
            AccountsRecord.entity_id == ClubsRecord.id,
            AccountsRecord.entity_type == "CLUB"
        )
    ).where(
        UsersRecord.id == user_id
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(check_query)
            return result.scalar()


async def select_half_account(account_id):
    query = select(
        AccountsRecord
    ).where(
        AccountsRecord.id == account_id
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalar()


async def select_half_accounts(start, limit):
    query = select(
        AccountsRecord
    ).where(
        AccountsRecord.id >= start
    ).limit(limit).order_by(asc(AccountsRecord.id))

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars().all()


async def select_last_entered_account(account_name: str, entity_id: int, entity_type: str):
    query = select(
        AccountsRecord
    ).where(
        and_(
            AccountsRecord.name == account_name,
            AccountsRecord.entity_id == entity_id,
            AccountsRecord.entity_type == entity_type
        )
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalar()


async def select_full_account(query):
    _data = {}
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)

            rows = result.all()

            _data["account"] = rows[0][0]
            _data["cards"] = [
                row[1] for row in rows if row[1]
            ]

    return _data


async def select_club_accounts(
        club_id: int, start: int, limit: int
) -> ScalarResult[AccountsRecord]:

    query = select(
        AccountsRecord
    ).where(
        and_(
            AccountsRecord.id >= start,
            AccountsRecord.entity_id == club_id,
            AccountsRecord.entity_type == "CLUB"
        )
    ).limit(limit).order_by(asc(AccountsRecord.id))

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars()
