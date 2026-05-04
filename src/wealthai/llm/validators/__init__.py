from collections.abc import Callable

from wealthai.llm.validators.create_sequence import validate_create_sequence
from wealthai.llm.validators.result import ValidationResult
from wealthai.llm.validators.update_ids import validate_update_ids
from wealthai.schemas import ChangeLog, ClientProfile

_validators: list[Callable[[ChangeLog, ClientProfile], ValidationResult]] = [
    validate_update_ids,
    validate_create_sequence,
]


def validate(changelog: ChangeLog, profile: ClientProfile) -> ValidationResult:
    result = ValidationResult()
    for validator in _validators:
        result = result + validator(changelog, profile)
    return result


__all__ = [
    "ValidationResult",
    "validate",
    "validate_create_sequence",
    "validate_update_ids",
]
