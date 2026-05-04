from pathlib import Path

import pytest

from wealthai.llm.validators.update_ids import validate_update_ids
from wealthai.schemas import ChangeLog, ClientProfile, PersonalDetailUpdate, RecordUpdate, UpdateSet

FIXTURES = Path(__file__).parents[3] / "input" / "clients"


@pytest.fixture
def james() -> ClientProfile:
    return ClientProfile.model_validate_json((FIXTURES / "client-001.json").read_text())


def test_known_ids_pass(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-001", field="value", old_value=87000, new_value=90000, evidence="...")],
            liabilities=[
                RecordUpdate(
                    id="liability-001", field="outstanding_balance", old_value=195000, new_value=0, evidence="..."
                )
            ],
            income_items=[
                RecordUpdate(id="income-001", field="amount", old_value=52000, new_value=68000, evidence="...")
            ],
            expense_items=[
                RecordUpdate(id="expense-002", field="amount", old_value=600, new_value=200, evidence="...")
            ],
        )
    )
    assert validate_update_ids(changelog, james).valid


def test_unknown_id_reported(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(assets=[RecordUpdate(id="asset-999", field="value", old_value=0, new_value=0, evidence="...")])
    )
    result = validate_update_ids(changelog, james)
    assert not result.valid
    assert any("asset-999" in e for e in result.errors)


def test_multiple_unknown_ids_all_reported(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-999", field="value", old_value=0, new_value=0, evidence="...")],
            expense_items=[RecordUpdate(id="expense-999", field="amount", old_value=0, new_value=0, evidence="...")],
        )
    )
    assert len(validate_update_ids(changelog, james).errors) == 2


def test_personal_detail_updates_skipped(james: ClientProfile):
    """PersonalDetailUpdate has no id — must not be checked."""
    changelog = ChangeLog(
        update=UpdateSet(
            personal_details=[
                PersonalDetailUpdate(field="email", old_value="a@b.com", new_value="c@d.com", evidence="...")
            ]
        )
    )
    assert validate_update_ids(changelog, james).valid


def test_empty_changelog_passes(james: ClientProfile):
    assert validate_update_ids(ChangeLog(), james).valid
