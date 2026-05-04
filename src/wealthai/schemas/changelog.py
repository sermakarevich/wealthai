from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from wealthai.schemas.common import Frequency

# ---------------------------------------------------------------------------
# Create items — new records to append to the client profile
# ---------------------------------------------------------------------------


class AssetCreate(BaseModel):
    type: str
    name: str
    value: float
    currency: str
    provider: str
    evidence: str


class LiabilityCreate(BaseModel):
    type: str
    provider: str
    outstanding_balance: float
    currency: str
    interest_rate_percent: float | None = None
    evidence: str


class IncomeItemCreate(BaseModel):
    source: str
    amount: float
    currency: str
    frequency: Frequency
    evidence: str


class ExpenseItemCreate(BaseModel):
    category: str
    amount: float
    currency: str
    frequency: Frequency
    evidence: str


class CreateSet(BaseModel):
    assets: list[AssetCreate] = Field(default_factory=list)
    liabilities: list[LiabilityCreate] = Field(default_factory=list)
    income_items: list[IncomeItemCreate] = Field(default_factory=list)
    expense_items: list[ExpenseItemCreate] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Update items — field-level patches on existing records
# ---------------------------------------------------------------------------


class PersonalDetailUpdate(BaseModel):
    """Patch to a scalar field on personal_details (no id — it is a single object)."""

    field: str
    old_value: Any
    new_value: Any
    evidence: str


class RecordUpdate(BaseModel):
    """Patch to a single field on an existing array record, identified by id."""

    id: str
    field: str
    old_value: Any
    new_value: Any
    evidence: str


class UpdateSet(BaseModel):
    personal_details: list[PersonalDetailUpdate] = Field(default_factory=list)
    assets: list[RecordUpdate] = Field(default_factory=list)
    liabilities: list[RecordUpdate] = Field(default_factory=list)
    income_items: list[RecordUpdate] = Field(default_factory=list)
    expense_items: list[RecordUpdate] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level change log
# ---------------------------------------------------------------------------


class ChangeLog(BaseModel):
    create: CreateSet = Field(default_factory=CreateSet)
    update: UpdateSet = Field(default_factory=UpdateSet)
