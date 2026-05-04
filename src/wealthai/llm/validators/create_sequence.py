from __future__ import annotations

from wealthai.llm.validators.result import ValidationResult
from wealthai.schemas import ChangeLog, ClientProfile

_PREFIX: dict[str, str] = {
    "assets": "asset",
    "liabilities": "liability",
    "income_items": "income",
    "expense_items": "expense",
}


def _extract_sequence(prefix: str, ids: list[str]) -> tuple[list[int], list[str]]:
    """Return sorted numeric suffixes and any malformed IDs."""
    nums: list[int] = []
    malformed: list[str] = []
    for id_ in ids:
        expected_prefix = f"{prefix}-"
        if not id_.startswith(expected_prefix):
            malformed.append(id_)
            continue
        suffix = id_[len(expected_prefix) :]
        if not suffix.isdigit():
            malformed.append(id_)
            continue
        nums.append(int(suffix))
    return sorted(nums), malformed


def validate_create_sequence(changelog: ChangeLog, profile: ClientProfile) -> ValidationResult:
    """
    Existing IDs for each entity type must form a gap-free consecutive sequence
    starting at 1, so the merger can safely assign the next IDs to new creates.
    """
    result = ValidationResult()

    entity_ids: dict[str, list[str]] = {
        "assets": [a.id for a in profile.assets],
        "liabilities": [li.id for li in profile.liabilities],
        "income_items": [inc.id for inc in profile.income_items],
        "expense_items": [exp.id for exp in profile.expense_items],
    }

    entity_creates: dict[str, int] = {
        "assets": len(changelog.create.assets),
        "liabilities": len(changelog.create.liabilities),
        "income_items": len(changelog.create.income_items),
        "expense_items": len(changelog.create.expense_items),
    }

    for entity, ids in entity_ids.items():
        if not ids and entity_creates[entity] == 0:
            continue

        prefix = _PREFIX[entity]
        nums, malformed = _extract_sequence(prefix, ids)

        for bad in malformed:
            result.errors.append(f"{entity} id {bad!r} does not match pattern {prefix}-NNN")

        for expected, actual in enumerate(nums, start=1):
            if actual != expected:
                result.errors.append(
                    f"Gap in {entity} sequence: expected {prefix}-{expected:03d}, found {prefix}-{actual:03d}"
                )
                break

    return result
