from datetime import datetime
from typing import List

from fastapi import HTTPException
from pydantic import BaseModel, Field

from src.security.security import fernet


class Card(BaseModel):
    id: int
    account_id: int
    card_number: str = Field()
    holder_name: str
    exp_date: str
    status: str

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


class Account(BaseModel):
    id: int
    uid: str
    name: str
    cards: List[Card] | None = None
    entity_type: str
    entity_id: int
    discount_rate: int = Field(min_value=0, max_value=100)
    status: str
