from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def __add__(self, other: ValidationResult) -> ValidationResult:
        return ValidationResult(errors=self.errors + other.errors)
