from datetime import datetime
from typing import List, Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator

from src.schema.validation import basic_string_validation
from src.security.security import fernet


class Card(BaseModel):
    id: int
    account_id: int
    card_number: str = Field()
    holder_name: str
    exp_date: str
    status: str
    class_name: str = "CARD"

    _encrypted: bool = False

    def validate_card(self):
        if self._encrypted:
            raise Exception("Details are encrypted")

        card_digits = len(self.card_number)
        if card_digits != 10 and card_digits != 13:
            raise HTTPException(status_code=422, detail="Invalid card number")

        if not self.card_number.isnumeric():
            raise HTTPException(
                422, "Invalid card number"
            )

        try:
            int(card_digits)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid card number")

        if not self.holder_name.isalpha():
            raise HTTPException(
                status_code=422,
                detail="Invalid holder name"
            )

        if len(self.exp_date) != 5:
            raise HTTPException(422, "Invalid exp date")

        try:
            datetime_object = datetime.strptime(self.exp_date, "%m/%y")
        except ValueError:
            raise HTTPException(
                422, "Invalid date format. Please use 'mm/yy'."
            )

    def encrypt(self):
        if self._encrypted:
            raise Exception("Details are encrypted")

        self.card_number = fernet.encrypt(
            self.card_number.encode()
        ).decode()
        self.holder_name = fernet.encrypt(
            self.holder_name.encode()
        ).decode()
        self.exp_date = fernet.encrypt(
            self.exp_date.encode()
        ).decode()

        self._encrypted = True

    def decrypt(self):
        if not self._encrypted:
            raise Exception("Details are not encrypted")

        self.card_number = fernet.decrypt(
            self.card_number.encode()
        ).decode()
        self.holder_name = fernet.decrypt(
            self.holder_name.encode()
        ).decode()
        self.exp_date = fernet.decrypt(
            self.exp_date.encode()
        ).decode()

        self._encrypted = False

    @classmethod
    @field_validator("card_number", mode="before")
    def card_number_validation(cls, value: str):
        return basic_string_validation(value, "card_number")

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
        return basic_string_validation(value, "exp_date")


class Account(BaseModel):
    id: int
    uid: str
    name: str
    cards: List[Card] | None = None
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
