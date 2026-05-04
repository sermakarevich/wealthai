from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from wealthai.schemas import ClientProfile, Frequency

FIXTURES = Path(__file__).parents[2] / "input" / "clients"


# ---------------------------------------------------------------------------
# Fixture parsing
# ---------------------------------------------------------------------------


def test_parse_james():
    profile = ClientProfile.model_validate_json((FIXTURES / "client-001.json").read_text())

    assert profile.id == "client-001"
    assert profile.personal_details.first_name == "James"
    assert profile.personal_details.date_of_birth == date(1985, 3, 22)
    assert profile.personal_details.address.city == "Bristol"
    assert profile.personal_details.address.postcode == "BS7 8TH"

    assert len(profile.assets) == 2
    scottish_widows = next(a for a in profile.assets if a.provider == "Scottish Widows")
    assert scottish_widows.type == "pension"
    assert scottish_widows.value == 87000

    marcus = next(a for a in profile.assets if "Marcus" in a.provider)
    assert marcus.type == "savings"
    assert marcus.value == 12000

    assert len(profile.liabilities) == 1
    mortgage = profile.liabilities[0]
    assert mortgage.provider == "Nationwide"
    assert mortgage.outstanding_balance == 195000
    assert mortgage.interest_rate_percent == 2.49

    assert profile.income_items[0].amount == 52000
    assert profile.income_items[0].frequency == Frequency.annually

    assert len(profile.expense_items) == 2
    childcare = next(e for e in profile.expense_items if e.category == "childcare")
    assert childcare.amount == 600


def test_parse_margaret():
    profile = ClientProfile.model_validate_json((FIXTURES / "client-002.json").read_text())

    assert profile.id == "client-002"
    assert profile.personal_details.last_name == "Chen"
    assert profile.personal_details.address.city == "Leeds"

    assert len(profile.assets) == 4
    providers = {a.provider for a in profile.assets}
    assert providers == {"NHS Pensions", "Standard Life", "Nationwide", "Hargreaves Lansdown"}

    # Barclaycard has optional limit field — should parse without errors
    barclaycard = next(lib for lib in profile.liabilities if lib.provider == "Barclaycard")
    assert barclaycard.limit == 5000
    assert barclaycard.outstanding_balance == 3200

    # HSBC mortgage has end_date, Barclaycard does not
    hsbc = next(lib for lib in profile.liabilities if lib.provider == "HSBC")
    assert hsbc.end_date == date(2031, 4, 1)
    assert barclaycard.end_date is None

    assert len(profile.expense_items) == 3


# ---------------------------------------------------------------------------
# Optional liability fields
# ---------------------------------------------------------------------------


def test_liability_all_optional_fields_absent():
    """Liability is valid without interest_rate_percent, end_date, or limit."""
    profile_data = {
        "id": "client-test",
        "personal_details": {
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
            "email": "test@example.com",
            "phone": "07000000000",
            "address": {},
        },
        "liabilities": [
            {
                "id": "liability-001",
                "type": "personal_loan",
                "provider": "Acme Bank",
                "outstanding_balance": 5000,
                "currency": "GBP",
            }
        ],
    }
    profile = ClientProfile.model_validate(profile_data)
    loan = profile.liabilities[0]
    assert loan.interest_rate_percent is None
    assert loan.end_date is None
    assert loan.limit is None


# ---------------------------------------------------------------------------
# Frequency validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", ["weekly", "monthly", "annually"])
def test_frequency_valid_values(value: str):
    assert Frequency(value).value == value


def test_frequency_rejects_invalid_value():
    from wealthai.schemas import IncomeItem

    with pytest.raises(ValidationError):
        IncomeItem(id="i-001", source="employment", amount=50000, currency="GBP", frequency="daily")


# ---------------------------------------------------------------------------
# Required field enforcement
# ---------------------------------------------------------------------------


def test_client_profile_missing_personal_details():
    with pytest.raises(ValidationError):
        ClientProfile.model_validate({"id": "client-x"})


def test_asset_missing_required_fields():
    from wealthai.schemas import Asset

    with pytest.raises(ValidationError):
        Asset.model_validate({"id": "asset-001", "type": "pension"})
