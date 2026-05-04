from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from wealthai.schemas.common import Frequency


class Address(BaseModel):
    address_line_1: str = ""
    address_line_2: str = ""
    city: str = ""
    postcode: str = ""
    country: str = ""


class PersonalDetails(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    email: str
    phone: str
    address: Address


class Asset(BaseModel):
    id: str
    type: str
    name: str
    value: float
    currency: str
    provider: str


class Liability(BaseModel):
    id: str
    type: str
    provider: str
    outstanding_balance: float
    currency: str
    interest_rate_percent: float | None = None
    end_date: date | None = None
    limit: float | None = None


class IncomeItem(BaseModel):
    id: str
    source: str
    amount: float
    currency: str
    frequency: Frequency


class ExpenseItem(BaseModel):
    id: str
    category: str
    amount: float
    currency: str
    frequency: Frequency


class ClientProfile(BaseModel):
    id: str
    personal_details: PersonalDetails
    assets: list[Asset] = Field(default_factory=list)
    liabilities: list[Liability] = Field(default_factory=list)
    income_items: list[IncomeItem] = Field(default_factory=list)
    expense_items: list[ExpenseItem] = Field(default_factory=list)
