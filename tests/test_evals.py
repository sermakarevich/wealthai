from __future__ import annotations

from wealthai.evals import _format_diff, score
from wealthai.schemas import (
    AssetCreate,
    ChangeLog,
    CreateSet,
    ExpenseItemCreate,
    LiabilityCreate,
    PersonalDetailUpdate,
    RecordUpdate,
    UpdateSet,
)

# ---------------------------------------------------------------------------
# Numeric tolerance on update value comparison
# ---------------------------------------------------------------------------


def test_update_value_int_vs_float_counts_as_match():
    actual = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-001", field="value", old_value=87000, new_value=95000, evidence="...")]
        )
    )
    expected = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-001", field="value", old_value=87000, new_value=95000.0, evidence="...")]
        )
    )
    result = score(actual, expected)
    assert result.value_accuracy == 1.0


def test_update_value_diff_shows_value_mismatch_only_when_truly_different():
    actual = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-001", field="value", old_value=87000, new_value=95000, evidence="...")]
        )
    )
    expected = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-001", field="value", old_value=87000, new_value=95000.0, evidence="...")]
        )
    )
    assert "value   X" not in _format_diff(actual, expected)


def test_update_numeric_difference_above_tolerance_fails():
    actual = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-001", field="value", old_value=87000, new_value=95000, evidence="...")]
        )
    )
    expected = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-001", field="value", old_value=87000, new_value=96000, evidence="...")]
        )
    )
    result = score(actual, expected)
    assert result.value_accuracy == 0.0


# ---------------------------------------------------------------------------
# Provider fuzzy match: "Aviva" vs "Aviva Pensions"
# ---------------------------------------------------------------------------


def test_asset_create_short_provider_matches_long():
    actual = ChangeLog(
        create=CreateSet(
            assets=[AssetCreate(type="pension", name="X", value=2000, currency="GBP", provider="Aviva", evidence="...")]
        )
    )
    expected = ChangeLog(
        create=CreateSet(
            assets=[
                AssetCreate(
                    type="pension", name="X", value=2000, currency="GBP", provider="Aviva Pensions", evidence="..."
                )
            ]
        )
    )
    result = score(actual, expected)
    assert result.creates.tp == 1
    assert result.creates.fp == 0
    assert result.creates.fn == 0


def test_asset_create_type_mismatch_overrides_text_similarity():
    actual = ChangeLog(
        create=CreateSet(
            assets=[AssetCreate(type="savings", name="X", value=1000, currency="GBP", provider="Aviva", evidence="...")]
        )
    )
    expected = ChangeLog(
        create=CreateSet(
            assets=[AssetCreate(type="pension", name="X", value=1000, currency="GBP", provider="Aviva", evidence="...")]
        )
    )
    result = score(actual, expected)
    assert result.creates.tp == 0
    assert result.creates.fp == 1
    assert result.creates.fn == 1


def test_asset_create_unrelated_provider_does_not_match():
    actual = ChangeLog(
        create=CreateSet(
            assets=[
                AssetCreate(
                    type="pension", name="X", value=1000, currency="GBP", provider="Standard Life", evidence="..."
                )
            ]
        )
    )
    expected = ChangeLog(
        create=CreateSet(
            assets=[AssetCreate(type="pension", name="X", value=1000, currency="GBP", provider="Aviva", evidence="...")]
        )
    )
    result = score(actual, expected)
    assert result.creates.tp == 0


# ---------------------------------------------------------------------------
# Near-miss surfaces in diff
# ---------------------------------------------------------------------------


def test_near_miss_surfaces_when_provider_unrelated_but_type_matches():
    actual = ChangeLog(
        create=CreateSet(
            liabilities=[
                LiabilityCreate(
                    type="loan", provider="Tesco Bank", outstanding_balance=15000, currency="GBP", evidence="..."
                )
            ]
        )
    )
    expected = ChangeLog(
        create=CreateSet(
            liabilities=[
                LiabilityCreate(
                    type="loan", provider="Tesco", outstanding_balance=15000, currency="GBP", evidence="..."
                )
            ]
        )
    )
    result = score(actual, expected)
    assert result.creates.tp == 1


# ---------------------------------------------------------------------------
# Expense / income create matching
# ---------------------------------------------------------------------------


def test_expense_create_amount_within_tolerance_matches():
    actual = ChangeLog(
        create=CreateSet(
            expense_items=[
                ExpenseItemCreate(
                    category="health_insurance", amount=68.0, currency="GBP", frequency="monthly", evidence="..."
                )
            ]
        )
    )
    expected = ChangeLog(
        create=CreateSet(
            expense_items=[
                ExpenseItemCreate(
                    category="health_insurance", amount=68, currency="GBP", frequency="monthly", evidence="..."
                )
            ]
        )
    )
    result = score(actual, expected)
    assert result.creates.tp == 1


def test_expense_create_category_mismatch_does_not_match():
    actual = ChangeLog(
        create=CreateSet(
            expense_items=[
                ExpenseItemCreate(category="childcare", amount=200, currency="GBP", frequency="monthly", evidence="...")
            ]
        )
    )
    expected = ChangeLog(
        create=CreateSet(
            expense_items=[
                ExpenseItemCreate(
                    category="after_school_club", amount=200, currency="GBP", frequency="monthly", evidence="..."
                )
            ]
        )
    )
    result = score(actual, expected)
    assert result.creates.tp == 0
    assert result.creates.fp == 1
    assert result.creates.fn == 1


# ---------------------------------------------------------------------------
# Personal detail updates
# ---------------------------------------------------------------------------


def test_personal_detail_update_matches():
    actual = ChangeLog(
        update=UpdateSet(
            personal_details=[
                PersonalDetailUpdate(
                    field="email",
                    old_value="old@example.com",
                    new_value="new@example.com",
                    evidence="...",
                )
            ]
        )
    )
    expected = ChangeLog(
        update=UpdateSet(
            personal_details=[
                PersonalDetailUpdate(
                    field="email",
                    old_value="old@example.com",
                    new_value="new@example.com",
                    evidence="...",
                )
            ]
        )
    )
    result = score(actual, expected)
    assert result.updates.tp == 1
    assert result.value_accuracy == 1.0


# ---------------------------------------------------------------------------
# Empty changelogs: perfect score (vacuously)
# ---------------------------------------------------------------------------


def test_empty_changelogs_score_perfectly():
    result = score(ChangeLog(), ChangeLog())
    assert result.creates.f1 == 1.0
    assert result.updates.f1 == 1.0
    assert result.value_accuracy == 1.0
