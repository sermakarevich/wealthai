from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from wealthai.io import load_changelog
from wealthai.schemas import ChangeLog

_PROJECT_ROOT = Path(__file__).parents[2]
_EXPECTED_DIR = _PROJECT_ROOT / "input" / "expected"


@dataclass
class CategoryScore:
    tp: int
    fp: int
    fn: int

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 1.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 1.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    def __str__(self) -> str:
        return (
            f"P={self.precision:.0%}  R={self.recall:.0%}  F1={self.f1:.0%}  (tp={self.tp} fp={self.fp} fn={self.fn})"  # noqa: E501
        )


@dataclass
class EvalResult:
    creates: CategoryScore
    updates: CategoryScore
    value_accuracy: float

    def __str__(self) -> str:
        return (
            f"Creates  {self.creates}\n"
            f"Updates  {self.updates}\n"
            f"Values   accuracy={self.value_accuracy:.0%} (of matched updates)"
        )


# ---------------------------------------------------------------------------
# Key extraction
# ---------------------------------------------------------------------------


def _create_keys(changelog: ChangeLog) -> set[tuple[str, ...]]:
    keys: set[tuple[str, ...]] = set()
    for a in changelog.create.assets:
        keys.add(("asset", a.type, a.provider.lower()))
    for lib in changelog.create.liabilities:
        keys.add(("liability", lib.type, lib.provider.lower()))
    for inc in changelog.create.income_items:
        keys.add(("income", str(inc.amount), inc.frequency))
    for exp in changelog.create.expense_items:
        keys.add(("expense", exp.category, str(exp.amount)))
    return keys


def _create_obj_map(changelog: ChangeLog) -> dict[tuple[str, ...], Any]:
    m: dict[tuple[str, ...], Any] = {}
    for a in changelog.create.assets:
        m[("asset", a.type, a.provider.lower())] = a
    for lib in changelog.create.liabilities:
        m[("liability", lib.type, lib.provider.lower())] = lib
    for inc in changelog.create.income_items:
        m[("income", str(inc.amount), inc.frequency)] = inc
    for exp in changelog.create.expense_items:
        m[("expense", exp.category, str(exp.amount))] = exp
    return m


def _obj_summary(obj: BaseModel) -> str:
    return "  ".join(f"{k}={v!r}" for k, v in obj.model_dump(exclude={"evidence"}).items() if v is not None)


def _update_map(changelog: ChangeLog) -> dict[tuple[str, str], object]:
    m: dict[tuple[str, str], object] = {}
    for pd_upd in changelog.update.personal_details:
        m[("personal_details", pd_upd.field)] = pd_upd.new_value
    for asset_upd in changelog.update.assets:
        m[(asset_upd.id, asset_upd.field)] = asset_upd.new_value
    for liability_upd in changelog.update.liabilities:
        m[(liability_upd.id, liability_upd.field)] = liability_upd.new_value
    for income_upd in changelog.update.income_items:
        m[(income_upd.id, income_upd.field)] = income_upd.new_value
    for expense_upd in changelog.update.expense_items:
        m[(expense_upd.id, expense_upd.field)] = expense_upd.new_value
    return m


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


def score(actual: ChangeLog, expected: ChangeLog) -> EvalResult:
    actual_creates = _create_keys(actual)
    expected_creates = _create_keys(expected)
    matched_creates = actual_creates & expected_creates
    creates = CategoryScore(
        tp=len(matched_creates),
        fp=len(actual_creates - expected_creates),
        fn=len(expected_creates - actual_creates),
    )

    actual_updates = _update_map(actual)
    expected_updates = _update_map(expected)
    matched_update_keys = set(actual_updates) & set(expected_updates)
    updates = CategoryScore(
        tp=len(matched_update_keys),
        fp=len(set(actual_updates) - set(expected_updates)),
        fn=len(set(expected_updates) - set(actual_updates)),
    )

    correct_values = sum(1 for k in matched_update_keys if actual_updates[k] == expected_updates[k])
    value_accuracy = correct_values / len(matched_update_keys) if matched_update_keys else 1.0

    return EvalResult(creates=creates, updates=updates, value_accuracy=value_accuracy)


def _format_diff(actual: ChangeLog, expected: ChangeLog) -> str:
    lines: list[str] = []

    actual_creates = _create_keys(actual)
    expected_creates = _create_keys(expected)
    actual_objs = _create_obj_map(actual)
    expected_objs = _create_obj_map(expected)
    for key in sorted(actual_creates - expected_creates):
        lines.append(f"  [creates FP] {_obj_summary(actual_objs[key])}")
    for key in sorted(expected_creates - actual_creates):
        lines.append(f"  [creates FN] {_obj_summary(expected_objs[key])}")

    actual_updates = _update_map(actual)
    expected_updates = _update_map(expected)
    for key in sorted(set(actual_updates) - set(expected_updates)):
        lines.append(f"  [update  FP] {key[0]}.{key[1]}  actual={actual_updates[key]!r}")
    for key in sorted(set(expected_updates) - set(actual_updates)):
        lines.append(f"  [update  FN] {key[0]}.{key[1]}  expected={expected_updates[key]!r}")
    for key in sorted(set(actual_updates) & set(expected_updates)):
        av, ev = actual_updates[key], expected_updates[key]
        if av != ev:
            lines.append(f"  [value   ✗] {key[0]}.{key[1]}  actual={av!r}  expected={ev!r}")

    return "\n".join(lines)


def run_eval(client_id: str) -> None:
    actual = load_changelog(client_id)
    expected = ChangeLog.model_validate_json((_EXPECTED_DIR / f"{client_id}.json").read_text())
    print(f"\n=== {client_id} ===")
    result = score(actual, expected)
    print(result)
    diff = _format_diff(actual, expected)
    if diff:
        print(diff)
