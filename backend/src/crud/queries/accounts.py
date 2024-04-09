from collections import defaultdict

from sqlalchemy import select, and_

from src.crud.engine import async_session
from src.crud.models import AccountsRecord, CardsRecord


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
