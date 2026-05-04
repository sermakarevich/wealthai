from __future__ import annotations

import re

from pydantic import BaseModel

from wealthai.schemas import (
    Asset,
    ChangeLog,
    ClientProfile,
    ExpenseItem,
    IncomeItem,
    Liability,
    PersonalDetails,
    PersonalDetailUpdate,
    RecordUpdate,
)

_ID_RE = re.compile(r"^([a-z]+)-(\d+)$")


def _next_id(prefix: str, existing: list[str]) -> str:
    nums = [int(m.group(2)) for raw in existing if (m := _ID_RE.match(raw)) and m.group(1) == prefix]
    return f"{prefix}-{(max(nums, default=0) + 1):03d}"


def _patch_personal(details: PersonalDetails, upd: PersonalDetailUpdate) -> PersonalDetails:
    parts = upd.field.split(".", 1)
    if parts[0] == "address" and len(parts) == 2:
        new_addr = details.address.model_copy(update={parts[1]: upd.new_value})
        return details.model_copy(update={"address": new_addr})
    return details.model_copy(update={upd.field: upd.new_value})


def _patch_by_id[T: BaseModel](records: list[T], upd: RecordUpdate) -> list[T]:
    return [r.model_copy(update={upd.field: upd.new_value}) if getattr(r, "id") == upd.id else r for r in records]


def apply_changelog(profile: ClientProfile, changelog: ChangeLog) -> ClientProfile:
    assets = list(profile.assets)
    for asset_c in changelog.create.assets:
        new_id = _next_id("asset", [a.id for a in assets])
        assets.append(Asset(id=new_id, **asset_c.model_dump(exclude={"evidence"})))

    liabilities = list(profile.liabilities)
    for liability_c in changelog.create.liabilities:
        new_id = _next_id("liability", [lib.id for lib in liabilities])
        liabilities.append(Liability(id=new_id, **liability_c.model_dump(exclude={"evidence"})))

    income_items = list(profile.income_items)
    for income_c in changelog.create.income_items:
        new_id = _next_id("income", [inc.id for inc in income_items])
        income_items.append(IncomeItem(id=new_id, **income_c.model_dump(exclude={"evidence"})))

    expense_items = list(profile.expense_items)
    for expense_c in changelog.create.expense_items:
        new_id = _next_id("expense", [exp.id for exp in expense_items])
        expense_items.append(ExpenseItem(id=new_id, **expense_c.model_dump(exclude={"evidence"})))

    personal_details = profile.personal_details
    for pd_upd in changelog.update.personal_details:
        personal_details = _patch_personal(personal_details, pd_upd)

    for asset_upd in changelog.update.assets:
        assets = _patch_by_id(assets, asset_upd)
    for liability_upd in changelog.update.liabilities:
        liabilities = _patch_by_id(liabilities, liability_upd)
    for income_upd in changelog.update.income_items:
        income_items = _patch_by_id(income_items, income_upd)
    for expense_upd in changelog.update.expense_items:
        expense_items = _patch_by_id(expense_items, expense_upd)

    return profile.model_copy(
        update={
            "personal_details": personal_details,
            "assets": assets,
            "liabilities": liabilities,
            "income_items": income_items,
            "expense_items": expense_items,
        }
    )
