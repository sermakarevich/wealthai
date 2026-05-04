from wealthai.llm.validators.old_values import validate_old_values
from wealthai.llm.validators.result import ValidationResult
from wealthai.llm.validators.update_ids import validate_update_ids
from wealthai.schemas import ChangeLog, ClientProfile


def validate(changelog: ChangeLog, profile: ClientProfile) -> ValidationResult:
    return validate_update_ids(changelog, profile) + validate_old_values(changelog, profile)


__all__ = [
    "ValidationResult",
    "validate",
    "validate_old_values",
    "validate_update_ids",
]
