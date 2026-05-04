from pathlib import Path

import pytest

from wealthai.llm.validators.old_values import validate_old_values
from wealthai.schemas import ChangeLog, ClientProfile, PersonalDetailUpdate, RecordUpdate, UpdateSet

FIXTURES = Path(__file__).parents[3] / "input" / "clients"


@pytest.fixture
def james() -> ClientProfile:
    return ClientProfile.model_validate_json((FIXTURES / "client-001.json").read_text())


@pytest.fixture
def margaret() -> ClientProfile:
    return ClientProfile.model_validate_json((FIXTURES / "client-002.json").read_text())


# ---------------------------------------------------------------------------
# personal details — flat fields
# ---------------------------------------------------------------------------


def test_correct_email_old_value_passes(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            personal_details=[
                PersonalDetailUpdate(
                    field="email",
                    old_value="james.whitfield@email.co.uk",
                    new_value="james.new@email.co.uk",
                    evidence="...",
                )
            ]
        )
    )
    assert validate_old_values(changelog, james).valid


def test_wrong_email_old_value_fails(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            personal_details=[
                PersonalDetailUpdate(
                    field="email", old_value="wrong@email.com", new_value="james.new@email.co.uk", evidence="..."
                )
            ]
        )
    )
    result = validate_old_values(changelog, james)
    assert not result.valid
    assert any("email" in e for e in result.errors)


# ---------------------------------------------------------------------------
# personal details — nested address via dot notation
# ---------------------------------------------------------------------------


def test_correct_address_postcode_passes(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            personal_details=[
                PersonalDetailUpdate(field="address.postcode", old_value="BS7 8TH", new_value="BS8 4AL", evidence="...")
            ]
        )
    )
    assert validate_old_values(changelog, james).valid


def test_wrong_address_postcode_fails(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            personal_details=[
                PersonalDetailUpdate(
                    field="address.postcode", old_value="SW1A 1AA", new_value="BS8 4AL", evidence="..."
                )
            ]
        )
    )
    result = validate_old_values(changelog, james)
    assert not result.valid
    assert any("postcode" in e for e in result.errors)


# ---------------------------------------------------------------------------
# array record fields
# ---------------------------------------------------------------------------


def test_correct_asset_value_passes(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-002", field="value", old_value=12000, new_value=8000, evidence="...")]
        )
    )
    assert validate_old_values(changelog, james).valid


def test_wrong_asset_value_fails(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-002", field="value", old_value=99999, new_value=8000, evidence="...")]
        )
    )
    result = validate_old_values(changelog, james)
    assert not result.valid
    assert any("asset-002" in e for e in result.errors)


def test_correct_income_amount_passes(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            income_items=[
                RecordUpdate(id="income-001", field="amount", old_value=52000, new_value=68000, evidence="...")
            ]
        )
    )
    assert validate_old_values(changelog, james).valid


def test_wrong_liability_balance_fails(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            liabilities=[
                RecordUpdate(id="liability-001", field="outstanding_balance", old_value=0, new_value=0, evidence="...")
            ]
        )
    )
    result = validate_old_values(changelog, james)
    assert not result.valid
    assert any("liability-001" in e for e in result.errors)


# ---------------------------------------------------------------------------
# unknown id is silently skipped (validate_update_ids owns that error)
# ---------------------------------------------------------------------------


def test_unknown_id_skipped(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(assets=[RecordUpdate(id="asset-999", field="value", old_value=0, new_value=0, evidence="...")])
    )
    assert validate_old_values(changelog, james).valid


# ---------------------------------------------------------------------------
# multiple mismatches all reported
# ---------------------------------------------------------------------------


def test_multiple_wrong_old_values_all_reported(margaret: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            income_items=[
                RecordUpdate(id="income-001", field="amount", old_value=99999, new_value=38800, evidence="...")
            ],
            assets=[RecordUpdate(id="asset-003", field="value", old_value=99999, new_value=26000, evidence="...")],
        )
    )
    result = validate_old_values(changelog, margaret)
    assert not result.valid
    assert len(result.errors) == 2


# ---------------------------------------------------------------------------
# empty changelog always passes
# ---------------------------------------------------------------------------


def test_empty_changelog_passes(james: ClientProfile):
    assert validate_old_values(ChangeLog(), james).valid
