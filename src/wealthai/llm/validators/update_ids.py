from __future__ import annotations

from wealthai.llm.validators.result import ValidationResult
from wealthai.schemas import ChangeLog, ClientProfile


def validate_update_ids(changelog: ChangeLog, profile: ClientProfile) -> ValidationResult:
    """Every ID referenced in an update item must exist in the client profile."""
    result = ValidationResult()

    existing: dict[str, set[str]] = {
        "assets": {a.id for a in profile.assets},
        "liabilities": {li.id for li in profile.liabilities},
        "income_items": {inc.id for inc in profile.income_items},
        "expense_items": {exp.id for exp in profile.expense_items},
    }

    checks = [
        ("assets", changelog.update.assets),
        ("liabilities", changelog.update.liabilities),
        ("income_items", changelog.update.income_items),
        ("expense_items", changelog.update.expense_items),
    ]

    for entity, updates in checks:
        for u in updates:
            if u.id not in existing[entity]:
                result.errors.append(f"Update on {entity} references unknown id {u.id!r} (field: {u.field!r})")

    return result
