from pathlib import Path

import pytest

from wealthai.llm.validators import validate
from wealthai.llm.validators.create_sequence import validate_create_sequence
from wealthai.schemas import AssetCreate, ChangeLog, ClientProfile, CreateSet, RecordUpdate, UpdateSet

FIXTURES = Path(__file__).parents[3] / "input" / "clients"


@pytest.fixture
def james() -> ClientProfile:
    return ClientProfile.model_validate_json((FIXTURES / "client-001.json").read_text())


@pytest.fixture
def margaret() -> ClientProfile:
    return ClientProfile.model_validate_json((FIXTURES / "client-002.json").read_text())


def test_consecutive_ids_pass(james: ClientProfile):
    # asset-001, asset-002 — clean sequence
    assert validate_create_sequence(ChangeLog(), james).valid


def test_full_margaret_profile_passes(margaret: ClientProfile):
    # asset-001..004, liability-001..002, income-001, expense-001..003
    assert validate_create_sequence(ChangeLog(), margaret).valid


def test_gap_in_sequence_reported(james: ClientProfile):
    data = james.model_dump()
    data["assets"][1]["id"] = "asset-003"  # 001, 003 — gap at 002
    gapped = ClientProfile.model_validate(data)

    result = validate_create_sequence(ChangeLog(), gapped)
    assert not result.valid
    assert any("asset" in e for e in result.errors)


def test_malformed_id_reported(james: ClientProfile):
    data = james.model_dump()
    data["assets"][0]["id"] = "asset-abc"
    bad = ClientProfile.model_validate(data)

    result = validate_create_sequence(ChangeLog(), bad)
    assert not result.valid
    assert any("asset-abc" in e for e in result.errors)


def test_empty_profile_passes():
    profile = ClientProfile.model_validate(
        {
            "id": "x",
            "personal_details": {
                "first_name": "A",
                "last_name": "B",
                "date_of_birth": "1990-01-01",
                "email": "a@b.com",
                "phone": "0",
                "address": {},
            },
        }
    )
    changelog = ChangeLog(
        create=CreateSet(
            assets=[
                AssetCreate(type="savings", name="ISA", value=1000, currency="GBP", provider="Vanguard", evidence="...")
            ]
        )
    )
    assert validate_create_sequence(changelog, profile).valid


# ---------------------------------------------------------------------------
# validate — combined
# ---------------------------------------------------------------------------


def test_validate_passes_clean_state(james: ClientProfile):
    changelog = ChangeLog(
        create=CreateSet(
            assets=[
                AssetCreate(type="pension", name="Aviva", value=2000, currency="GBP", provider="Aviva", evidence="...")
            ]
        ),
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-002", field="value", old_value=12000, new_value=8000, evidence="...")]
        ),
    )
    assert validate(changelog, james).valid


def test_validate_collects_errors_from_both(james: ClientProfile):
    data = james.model_dump()
    data["assets"][1]["id"] = "asset-003"  # gap in sequence
    gapped = ClientProfile.model_validate(data)

    changelog = ChangeLog(
        update=UpdateSet(assets=[RecordUpdate(id="asset-999", field="value", old_value=0, new_value=0, evidence="...")])
    )
    result = validate(changelog, gapped)
    assert not result.valid
    assert len(result.errors) >= 2
