import pytest
from pydantic import ValidationError

from wealthai.schemas import (
    AssetCreate,
    ChangeLog,
    CreateSet,
    ExpenseItemCreate,
    Frequency,
    IncomeItemCreate,
    LiabilityCreate,
    PersonalDetailUpdate,
    RecordUpdate,
    UpdateSet,
)

# ---------------------------------------------------------------------------
# Transcript 1 — James: individual change scenarios
# ---------------------------------------------------------------------------


def test_create_aviva_pension():
    """New employer pension created after James joins Dyson."""
    asset = AssetCreate(
        type="pension",
        name="Dyson Workplace Pension",
        value=2000,
        currency="GBP",
        provider="Aviva",
        evidence="Dyson auto-enrolled me into their scheme with Aviva. "
        "I've been contributing for about three months now, so there's probably around two thousand in there so far.",
    )
    assert asset.type == "pension"
    assert asset.provider == "Aviva"
    assert asset.value == 2000


def test_create_vanguard_isa():
    """New Vanguard stocks and shares ISA created in September."""
    asset = AssetCreate(
        type="investment",
        name="Stocks and Shares ISA",
        value=3000,
        currency="GBP",
        provider="Vanguard",
        evidence="I'm also paying into a Vanguard stocks and shares ISA — "
        "I set it up in September, putting in five hundred a month. It's worth about three thousand at the moment.",
    )
    assert asset.provider == "Vanguard"
    assert asset.value == 3000


def test_create_tesco_home_improvement_loan():
    """New Tesco Bank personal loan."""
    liability = LiabilityCreate(
        type="personal_loan",
        provider="Tesco Bank",
        outstanding_balance=15000,
        currency="GBP",
        interest_rate_percent=6.9,
        evidence="we took out a home improvement loan with Tesco Bank — "
        "fifteen thousand over five years at six point nine percent.",
    )
    assert liability.outstanding_balance == 15000
    assert liability.interest_rate_percent == 6.9


def test_update_address():
    """James moved house — all address sub-fields updated."""
    updates = [
        PersonalDetailUpdate(
            field="address.address_line_1",
            old_value="14 Elm Grove",
            new_value="28 Oakfield Road",
            evidence="we moved house back in November — we're now at 28 Oakfield Road in Clifton",
        ),
        PersonalDetailUpdate(
            field="address.city",
            old_value="Bristol",
            new_value="Clifton",
            evidence="we're now at 28 Oakfield Road in Clifton, still Bristol",
        ),
        PersonalDetailUpdate(
            field="address.postcode",
            old_value="BS7 8TH",
            new_value="BS8 4AL",
            evidence="postcode BS8 4AL",
        ),
    ]
    assert all(u.new_value for u in updates)


def test_update_salary():
    """James got a salary bump at Dyson."""
    update = RecordUpdate(
        id="income-001",
        field="amount",
        old_value=52000,
        new_value=68000,
        evidence="I've joined Dyson as a Senior Engineering Manager. The salary is sixty-eight thousand a year.",
    )
    assert update.old_value == 52000
    assert update.new_value == 68000


def test_mortgage_migration_zero_old_create_new():
    """
    Nationwide mortgage replaced by Halifax.
    Old record is zeroed out; new Halifax record is created.
    """
    zero_old = RecordUpdate(
        id="liability-001",
        field="outstanding_balance",
        old_value=195000,
        new_value=0,
        evidence="We sold the old place and got a new mortgage with Halifax.",
    )
    new_mortgage = LiabilityCreate(
        type="mortgage",
        provider="Halifax",
        outstanding_balance=275000,
        currency="GBP",
        interest_rate_percent=4.19,
        evidence="new mortgage with Halifax. The outstanding balance is two hundred and seventy-five thousand, "
        "fixed at four point one nine percent for five years, so it runs until 2030.",
    )
    assert zero_old.new_value == 0
    assert new_mortgage.outstanding_balance == 275000
    assert new_mortgage.interest_rate_percent == 4.19


def test_update_childcare_expense():
    """Childcare dropped after daughter started school."""
    update = RecordUpdate(
        id="expense-002",
        field="amount",
        old_value=600,
        new_value=200,
        evidence="our daughter started school in September so that cost has dropped. "
        "We're only paying for the after-school club now, about two hundred a month.",
    )
    assert update.old_value == 600
    assert update.new_value == 200


# ---------------------------------------------------------------------------
# Transcript 2 — Margaret: individual change scenarios
# ---------------------------------------------------------------------------


def test_update_salary_part_time():
    """Margaret reduced to 4 days/week."""
    update = RecordUpdate(
        id="income-001",
        field="amount",
        old_value=48500,
        new_value=38800,
        evidence="I've dropped to four days a week from January. "
        "So my salary has gone down — it's now thirty-eight thousand eight hundred.",
    )
    assert update.new_value == 38800


def test_pension_transfer_zero_standard_life():
    """Standard Life pension transferred to Fidelity — old record zeroed."""
    zero_old = RecordUpdate(
        id="asset-002",
        field="value",
        old_value=45000,
        new_value=0,
        evidence="the Standard Life one — I moved it to Fidelity back in September.",
    )
    new_pension = AssetCreate(
        type="pension",
        name="Private Pension",
        value=49000,
        currency="GBP",
        provider="Fidelity",
        evidence="The transfer went through at about forty-seven thousand "
        "and it's sitting at around forty-nine thousand now.",
    )
    assert zero_old.new_value == 0
    assert new_pension.provider == "Fidelity"
    assert new_pension.value == 49000


def test_barclaycard_paid_off():
    """Barclaycard cleared — balance zeroed, no delete operation in schema."""
    update = RecordUpdate(
        id="liability-002",
        field="outstanding_balance",
        old_value=3200,
        new_value=0,
        evidence="I paid off the Barclaycard completely in October. Used some of the savings to clear it.",
    )
    assert update.new_value == 0


def test_create_bupa_health_insurance():
    """Margaret started a new BUPA health insurance expense."""
    expense = ExpenseItemCreate(
        category="health_insurance",
        amount=68,
        currency="GBP",
        frequency=Frequency.monthly,
        evidence="I started paying into a private health insurance plan with Bupa. It's sixty-eight pounds a month.",
    )
    assert expense.amount == 68
    assert expense.frequency == Frequency.monthly


def test_update_email():
    """Margaret changed her email address."""
    update = PersonalDetailUpdate(
        field="email",
        old_value="margaret.chen@btinternet.com",
        new_value="margaret.chen@gmail.com",
        evidence="I changed my email to margaret.chen@gmail.com. The BT one was getting too much spam.",
    )
    assert update.new_value == "margaret.chen@gmail.com"


# ---------------------------------------------------------------------------
# ChangeLog composition and defaults
# ---------------------------------------------------------------------------


def test_empty_changelog_has_valid_defaults():
    log = ChangeLog()
    assert log.create.assets == []
    assert log.create.liabilities == []
    assert log.update.personal_details == []
    assert log.update.income_items == []


def test_full_changelog_serialises_to_dict():
    log = ChangeLog(
        create=CreateSet(
            assets=[
                AssetCreate(
                    type="pension",
                    name="Dyson Workplace Pension",
                    value=2000,
                    currency="GBP",
                    provider="Aviva",
                    evidence="Dyson auto-enrolled me into their scheme with Aviva.",
                )
            ]
        ),
        update=UpdateSet(
            personal_details=[
                PersonalDetailUpdate(
                    field="address.postcode",
                    old_value="BS7 8TH",
                    new_value="BS8 4AL",
                    evidence="postcode BS8 4AL",
                )
            ],
            assets=[
                RecordUpdate(
                    id="asset-002",
                    field="value",
                    old_value=12000,
                    new_value=8000,
                    evidence="It's sitting at around eight thousand now.",
                )
            ],
        ),
    )
    data = log.model_dump()
    assert data["create"]["assets"][0]["provider"] == "Aviva"
    assert data["update"]["personal_details"][0]["field"] == "address.postcode"
    assert data["update"]["assets"][0]["id"] == "asset-002"


# ---------------------------------------------------------------------------
# Evidence field is required
# ---------------------------------------------------------------------------


def test_asset_create_missing_evidence_raises():
    with pytest.raises(ValidationError):
        AssetCreate(type="pension", name="Test", value=1000, currency="GBP", provider="Test Co")


def test_record_update_missing_evidence_raises():
    with pytest.raises(ValidationError):
        RecordUpdate(id="asset-001", field="value", old_value=1000, new_value=2000)


def test_income_create_missing_evidence_raises():
    with pytest.raises(ValidationError):
        IncomeItemCreate(source="employment", amount=50000, currency="GBP", frequency=Frequency.annually)
