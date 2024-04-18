from typing import List

from src.schema.accounts import Account, Card


class AccountsFactory:
    @staticmethod
    def get_account(mp: dict) -> Account:
        account_record = mp["account"]
        card_records = mp["cards"]

        cards = [
            AccountsFactory.get_card(x) for x in card_records
        ]

        account = AccountsFactory.get_half_account(account_record)
        account.cards = cards

        return account

    @staticmethod
    def get_accounts(items) -> List[Account]:
        return [
            AccountsFactory.get_account(c) for c in items
        ]

    @staticmethod
    def get_card(record) -> Card:
        card = Card(
            id=record.card_id,
            account_id=record.account_id,
            card_number=record.card_number,
            holder_name=record.holder_name,
            exp_date=record.exp_date,
            status=record.status,
        )
        card._encrypted = True
        return card

    @staticmethod
    def get_half_account(record) -> Account:
        return Account(
            id=record.id,
            uid=record.account_uid,
            name=record.name,
            entity_type=record.entity_type,
            discount_rate=record.discount_rate,
            entity_id=record.entity_id,
            status=record.status,
            balance=record.balance
        )

    @staticmethod
    def get_half_accounts(records) -> List[Account]:
        return [
            AccountsFactory.get_half_account(x) for x in records
        ]
