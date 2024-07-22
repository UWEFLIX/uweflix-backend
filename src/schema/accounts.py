import base64
import hashlib
from datetime import datetime
from typing import List, Literal

from cryptography.fernet import Fernet
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
from pydantic_extra_types.payment import PaymentCardNumber

from src.schema.validation import basic_string_validation


class Card(BaseModel):
    """Encrypted Card data"""
    id: int
    account_id: int
    card_number: str
    holder_name: str
    exp_date: str
    status: str
    class_name: str = "CARD"


class CardInput(BaseModel):
    """Unencrypted Card data"""
    id: int
    account_id: int
    card_number: PaymentCardNumber
    holder_name: str
    exp_date: str
    status: str
    user_password: str = Field(exclude=True)
    class_name: str = "CardInput"

    @classmethod
    @field_validator("holder_name", mode="before")
    def holder_name_validation(cls, value: str):
        return basic_string_validation(value, "holder_name")

    @classmethod
    @field_validator("status", mode="before")
    def status_validation(cls, value: str):
        return basic_string_validation(value, "status")

    @classmethod
    @field_validator("exp_date", mode="before")
    def exp_date_validation(cls, value: str):
        value = basic_string_validation(value, "exp_date")

        if len(value) != 5:
            raise ValueError("Invalid length of exp_date")

        datetime.strptime(
            f"01/{value}",
            "%d/%m/%y"
        )

        return value

    @staticmethod
    def encrypt(string: str, fernet: Fernet) -> str:
        return fernet.encrypt(string.encode()).decode()

    @staticmethod
    def decrypt(cipher_text: str, fernet: Fernet) -> str:
        return fernet.decrypt(cipher_text.encode()).decode()

    def card(self) -> Card:
        hash_object = hashlib.sha256(
            self.user_password.encode()
        )
        digest = hash_object.digest()
        digest = base64.urlsafe_b64encode(digest[:32])
        fernet = Fernet(digest)
        return Card(
            id=self.id,
            account_id=self.account_id,
            card_number=CardInput.encrypt(self.card_number, fernet),
            holder_name=CardInput.encrypt(self.holder_name, fernet),
            exp_date=CardInput.encrypt(self.exp_date, fernet),
            status=self.status,
        )


class Account(BaseModel):
    id: int
    uid: str
    name: str
    entity_type: str
    entity_id: int
    discount_rate: int = Field(min_value=0, max_value=100)
    status: str
    balance: float
    class_name: str = "ACCOUNT"

    @classmethod
    @field_validator("name", mode="before")
    def name_validation(cls, value: str):
        return basic_string_validation(value, "name")

    @classmethod
    @field_validator("status", mode="before")
    def status_validation(cls, value: str):
        return basic_string_validation(value, "status")


class TopUp(BaseModel):
    card_id: int
    account_id: int
    amount: float
    user_password: str
