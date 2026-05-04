from __future__ import annotations

from typing import Any, cast

from wealthai.llm.validators.result import ValidationResult
from wealthai.schemas import ChangeLog, ClientProfile


def _personal_value(profile: ClientProfile, field: str) -> object:
    data = profile.personal_details.model_dump(mode="json")
    parts = field.split(".", 1)
    if len(parts) == 2:
        nested = data.get(parts[0])
        return nested.get(parts[1]) if isinstance(nested, dict) else None
    return data.get(field)


def validate_old_values(changelog: ChangeLog, profile: ClientProfile) -> ValidationResult:
    """old_value on every update item must match the current value in the profile."""
    result = ValidationResult()

    for upd in changelog.update.personal_details:
        actual = _personal_value(profile, upd.field)
        if actual != upd.old_value:
            result.errors.append(
                f"personal_details.{upd.field}: old_value {upd.old_value!r} does not match profile value {actual!r}"
            )

    entity_records: dict[str, list[Any]] = {
        "assets": cast(list[Any], profile.assets),
        "liabilities": cast(list[Any], profile.liabilities),
        "income_items": cast(list[Any], profile.income_items),
        "expense_items": cast(list[Any], profile.expense_items),
    }

    for entity, records in entity_records.items():
        by_id = {r.id: r.model_dump(mode="json") for r in records}
        for upd in getattr(changelog.update, entity):
            record = by_id.get(upd.id)
            if record is None:
                continue  # already caught by validate_update_ids
            actual = record.get(upd.field)
            if actual != upd.old_value:
                result.errors.append(
                    f"{entity}[{upd.id}].{upd.field}: old_value {upd.old_value!r} "
                    f"does not match profile value {actual!r}"
                )

    return result
