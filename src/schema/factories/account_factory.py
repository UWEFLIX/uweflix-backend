import base64
import hashlib
from typing import List

from cryptography.fernet import Fernet

from src.schema.accounts import Account, Card, CardInput


class AccountsFactory:
    @staticmethod
    def get_account(mp: dict) -> Account:
        account_record = mp["account"]

        account = AccountsFactory.get_half_account(account_record)

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
        return card

    @staticmethod
    def get_cards(records) -> List[Card]:
        return [
            AccountsFactory.get_card(record) for record in records
        ]

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

    @staticmethod
    def get_card_input(card: Card, password: str) -> CardInput:
        hash_object = hashlib.sha256(password.encode())
        digest = hash_object.digest()
        digest = base64.urlsafe_b64encode(digest[:32])
        fernet = Fernet(digest)
        return CardInput(
            id=card.id,
            account_id=card.account_id,
            card_number=CardInput.decrypt(card.card_number, fernet),
            holder_name=CardInput.decrypt(card.holder_name, fernet),
            exp_date=CardInput.decrypt(card.exp_date, fernet),
            status=card.status,
            user_password="",
        )
