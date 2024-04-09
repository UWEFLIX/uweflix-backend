from typing import List

from src.schema.users import Card, Account


class AccountsFactory:
    @staticmethod
    def get_account(mp: dict) -> Account:
        account_record = mp["account"]
        card_records = mp["cards"]

        cards = [
            Card(
                id=x.card_id,
                card_number=x.card_number,
                holder_name=x.holder_name,
                exp_date=x.exp_date,
                status=x.status,
            ) for x in card_records
        ]

        return Account(
            id=account_record.id,
            uid=account_record.account_uid,
            name=account_record.name,
            entity_type=account_record.entity_type,
            discount_rate=account_record.discount_rate,
            cards=cards
        )

    @staticmethod
    def get_accounts(mps: dict) -> List[Account]:
        return [
            AccountsFactory.get_account(mp) for account_id, mp in mps.items()
        ]

    @staticmethod
    def get_card(record) -> Card:
        return Card(
            id=record.card_id,
            card_number=record.card_number,
            holder_name=record.holder_name,
            exp_date=record.exp_date,
            status=record.status,
        )
