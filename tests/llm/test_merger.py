from pathlib import Path

import pytest

from wealthai.llm.merger import apply_changelog
from wealthai.schemas import (
    AssetCreate,
    ChangeLog,
    ClientProfile,
    CreateSet,
    LiabilityCreate,
    PersonalDetailUpdate,
    RecordUpdate,
    UpdateSet,
)

FIXTURES = Path(__file__).parents[2] / "input" / "clients"


@pytest.fixture
def james() -> ClientProfile:
    return ClientProfile.model_validate_json((FIXTURES / "client-001.json").read_text())


# ---------------------------------------------------------------------------
# creates
# ---------------------------------------------------------------------------


def test_create_asset_gets_next_id(james: ClientProfile):
    changelog = ChangeLog(
        create=CreateSet(
            assets=[
                AssetCreate(type="savings", name="ISA", value=5000, currency="GBP", provider="Vanguard", evidence="...")
            ]
        )
    )
    result = apply_changelog(james, changelog)
    new_asset = result.assets[-1]
    assert new_asset.id == "asset-003"
    assert new_asset.name == "ISA"
    assert new_asset.value == 5000


def test_create_liability_gets_next_id(james: ClientProfile):
    changelog = ChangeLog(
        create=CreateSet(
            liabilities=[
                LiabilityCreate(type="loan", provider="HSBC", outstanding_balance=10000, currency="GBP", evidence="...")
            ]
        )
    )
    result = apply_changelog(james, changelog)
    new_liability = result.liabilities[-1]
    assert new_liability.id == "liability-002"
    assert new_liability.provider == "HSBC"


def test_multiple_creates_get_sequential_ids(james: ClientProfile):
    changelog = ChangeLog(
        create=CreateSet(
            assets=[
                AssetCreate(type="pension", name="A", value=1000, currency="GBP", provider="Aviva", evidence="..."),
                AssetCreate(
                    type="pension", name="B", value=2000, currency="GBP", provider="Legal & General", evidence="..."
                ),
            ]
        )
    )
    result = apply_changelog(james, changelog)
    ids = [a.id for a in result.assets]
    assert "asset-003" in ids
    assert "asset-004" in ids


# ---------------------------------------------------------------------------
# record updates
# ---------------------------------------------------------------------------


def test_update_asset_value(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-001", field="value", old_value=87000, new_value=95000, evidence="...")]
        )
    )
    result = apply_changelog(james, changelog)
    updated = next(a for a in result.assets if a.id == "asset-001")
    assert updated.value == 95000


def test_update_leaves_other_records_unchanged(james: ClientProfile):
    original_value = next(a for a in james.assets if a.id == "asset-002").value
    changelog = ChangeLog(
        update=UpdateSet(
            assets=[RecordUpdate(id="asset-001", field="value", old_value=87000, new_value=95000, evidence="...")]
        )
    )
    result = apply_changelog(james, changelog)
    assert next(a for a in result.assets if a.id == "asset-002").value == original_value


# ---------------------------------------------------------------------------
# personal detail updates
# ---------------------------------------------------------------------------


def test_update_personal_detail_flat_field(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            personal_details=[
                PersonalDetailUpdate(
                    field="email", old_value="james@example.com", new_value="james.new@example.com", evidence="..."
                )
            ]
        )
    )
    result = apply_changelog(james, changelog)
    assert result.personal_details.email == "james.new@example.com"


def test_update_personal_detail_nested_address(james: ClientProfile):
    changelog = ChangeLog(
        update=UpdateSet(
            personal_details=[
                PersonalDetailUpdate(field="address.postcode", old_value="BS7 8TH", new_value="BS8 4AL", evidence="...")
            ]
        )
    )
    result = apply_changelog(james, changelog)
    assert result.personal_details.address.postcode == "BS8 4AL"


# ---------------------------------------------------------------------------
# no mutation
# ---------------------------------------------------------------------------


def test_empty_changelog_returns_equivalent_profile(james: ClientProfile):
    result = apply_changelog(james, ChangeLog())
    assert result.model_dump() == james.model_dump()
