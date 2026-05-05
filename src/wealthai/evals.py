from __future__ import annotations

import logging
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from wealthai.io import load_changelog
from wealthai.schemas import (
    AssetCreate,
    ChangeLog,
    ExpenseItemCreate,
    IncomeItemCreate,
    LiabilityCreate,
)

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parents[2]
_EXPECTED_DIR = _PROJECT_ROOT / "input" / "expected"

# Numbers within 1% relative or 0.01 absolute are considered equal.
_AMOUNT_REL_TOL = 0.01
_AMOUNT_ABS_TOL = 0.01

# Token-overlap similarity above this counts as a match.
_MATCH_THRESHOLD = 0.5

# Below the match threshold but above this, FP/FN are paired up as near-misses
# in the diff so the reviewer sees they are likely the same item with wording drift.
_NEAR_MISS_THRESHOLD = 0.1


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
            f"P={self.precision:.0%}  R={self.recall:.0%}  F1={self.f1:.0%}  (tp={self.tp} fp={self.fp} fn={self.fn})"
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
# Similarity helpers
# ---------------------------------------------------------------------------


def _amounts_close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=_AMOUNT_REL_TOL, abs_tol=_AMOUNT_ABS_TOL)


def _text_similarity(a: str, b: str) -> float:
    """Token-overlap similarity on casefolded text. Asymmetric: a short version
    (e.g. 'Aviva') of a longer phrase ('Aviva Pensions') scores 1.0 because we
    divide by the smaller token count."""
    ta = set(a.casefold().split())
    tb = set(b.casefold().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def _values_equal(a: object, b: object) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, int | float) and isinstance(b, int | float):
        return _amounts_close(float(a), float(b))
    return a == b


def _asset_similarity(a: AssetCreate, b: AssetCreate) -> float:
    if a.type != b.type:
        return 0.0
    return _text_similarity(a.provider, b.provider)


def _liability_similarity(a: LiabilityCreate, b: LiabilityCreate) -> float:
    if a.type != b.type:
        return 0.0
    return _text_similarity(a.provider, b.provider)


def _income_similarity(a: IncomeItemCreate, b: IncomeItemCreate) -> float:
    if a.frequency != b.frequency or a.source != b.source:
        return 0.0
    return 1.0 if _amounts_close(a.amount, b.amount) else 0.0


def _expense_similarity(a: ExpenseItemCreate, b: ExpenseItemCreate) -> float:
    if a.frequency != b.frequency or a.category != b.category:
        return 0.0
    return 1.0 if _amounts_close(a.amount, b.amount) else 0.0


# ---------------------------------------------------------------------------
# Greedy bipartite matcher
# ---------------------------------------------------------------------------


def _match_items[T: BaseModel](
    actual: Sequence[T],
    expected: Sequence[T],
    similarity: Callable[[T, T], float],
) -> tuple[list[tuple[T, T]], list[T], list[T]]:
    """For each actual item, claim the best-fitting unclaimed expected item above threshold.

    Returns (matched_pairs, unmatched_actual, unmatched_expected).
    """
    available = list(expected)
    matched: list[tuple[T, T]] = []
    unmatched_actual: list[T] = []
    for a in actual:
        best_idx = -1
        best_score = _MATCH_THRESHOLD
        for i, e in enumerate(available):
            s = similarity(a, e)
            if s > best_score:
                best_score, best_idx = s, i
        if best_idx >= 0:
            matched.append((a, available.pop(best_idx)))
        else:
            unmatched_actual.append(a)
    return matched, unmatched_actual, available


# ---------------------------------------------------------------------------
# Per-category create scoring
# ---------------------------------------------------------------------------


@dataclass
class _CreateMatch:
    label: str
    matched: list[tuple[BaseModel, BaseModel]]
    fp: list[BaseModel]
    fn: list[BaseModel]
    similarity: Callable[[BaseModel, BaseModel], float]


def _score_creates(actual: ChangeLog, expected: ChangeLog) -> list[_CreateMatch]:
    pairs: list[_CreateMatch] = []
    a_m, a_fp, a_fn = _match_items(actual.create.assets, expected.create.assets, _asset_similarity)
    pairs.append(
        _CreateMatch(
            "asset",
            list(a_m),
            list(a_fp),
            list(a_fn),
            _asset_similarity,  # type: ignore[arg-type]
        )
    )
    li_m, li_fp, li_fn = _match_items(actual.create.liabilities, expected.create.liabilities, _liability_similarity)
    pairs.append(
        _CreateMatch(
            "liability",
            list(li_m),
            list(li_fp),
            list(li_fn),
            _liability_similarity,  # type: ignore[arg-type]
        )
    )
    in_m, in_fp, in_fn = _match_items(actual.create.income_items, expected.create.income_items, _income_similarity)
    pairs.append(
        _CreateMatch(
            "income",
            list(in_m),
            list(in_fp),
            list(in_fn),
            _income_similarity,  # type: ignore[arg-type]
        )
    )
    ex_m, ex_fp, ex_fn = _match_items(actual.create.expense_items, expected.create.expense_items, _expense_similarity)
    pairs.append(
        _CreateMatch(
            "expense",
            list(ex_m),
            list(ex_fp),
            list(ex_fn),
            _expense_similarity,  # type: ignore[arg-type]
        )
    )
    return pairs


def _create_score(matches: list[_CreateMatch]) -> CategoryScore:
    return CategoryScore(
        tp=sum(len(m.matched) for m in matches),
        fp=sum(len(m.fp) for m in matches),
        fn=sum(len(m.fn) for m in matches),
    )


# ---------------------------------------------------------------------------
# Update mapping
# ---------------------------------------------------------------------------


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
    creates = _create_score(_score_creates(actual, expected))

    actual_updates = _update_map(actual)
    expected_updates = _update_map(expected)
    matched_keys = set(actual_updates) & set(expected_updates)
    updates = CategoryScore(
        tp=len(matched_keys),
        fp=len(set(actual_updates) - set(expected_updates)),
        fn=len(set(expected_updates) - set(actual_updates)),
    )

    correct = sum(1 for k in matched_keys if _values_equal(actual_updates[k], expected_updates[k]))
    value_accuracy = correct / len(matched_keys) if matched_keys else 1.0

    return EvalResult(creates=creates, updates=updates, value_accuracy=value_accuracy)


# ---------------------------------------------------------------------------
# Diff formatting (with near-miss surfacing)
# ---------------------------------------------------------------------------


def _obj_summary(obj: BaseModel) -> str:
    return "  ".join(f"{k}={v!r}" for k, v in obj.model_dump(exclude={"evidence"}).items() if v is not None)


def _format_create_section(match: _CreateMatch) -> list[str]:
    """Show FP/FN for a category, pairing them as ~MISS when their similarity is non-trivial."""
    lines: list[str] = []
    fn_remaining = list(match.fn)
    for fp in match.fp:
        best_idx = -1
        best_score = _NEAR_MISS_THRESHOLD
        for i, fn in enumerate(fn_remaining):
            s = match.similarity(fp, fn)
            if s > best_score:
                best_score, best_idx = s, i
        if best_idx >= 0:
            fn = fn_remaining.pop(best_idx)
            lines.append(f"  [{match.label} ~MISS sim={best_score:.2f}]")
            lines.append(f"      actual:   {_obj_summary(fp)}")
            lines.append(f"      expected: {_obj_summary(fn)}")
        else:
            lines.append(f"  [{match.label} create FP] {_obj_summary(fp)}")
    for fn in fn_remaining:
        lines.append(f"  [{match.label} create FN] {_obj_summary(fn)}")
    return lines


def _format_diff(actual: ChangeLog, expected: ChangeLog) -> str:
    lines: list[str] = []
    for match in _score_creates(actual, expected):
        lines.extend(_format_create_section(match))

    actual_updates = _update_map(actual)
    expected_updates = _update_map(expected)
    for key in sorted(set(actual_updates) - set(expected_updates)):
        lines.append(f"  [update  FP] {key[0]}.{key[1]}  actual={actual_updates[key]!r}")
    for key in sorted(set(expected_updates) - set(actual_updates)):
        lines.append(f"  [update  FN] {key[0]}.{key[1]}  expected={expected_updates[key]!r}")
    for key in sorted(set(actual_updates) & set(expected_updates)):
        av, ev = actual_updates[key], expected_updates[key]
        if not _values_equal(av, ev):
            lines.append(f"  [value   X] {key[0]}.{key[1]}  actual={av!r}  expected={ev!r}")

    return "\n".join(lines)


def run_evals(client_id: str) -> None:
    actual = load_changelog(client_id)
    expected = ChangeLog.model_validate_json((_EXPECTED_DIR / f"{client_id}.json").read_text())
    logger.info("=== %s ===", client_id)
    result = score(actual, expected)
    logger.info("%s", result)
    diff = _format_diff(actual, expected)
    if diff:
        logger.info("%s", diff)
