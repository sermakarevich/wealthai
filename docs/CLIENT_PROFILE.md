# Client Profiles

## Scenario 1 — James Whitfield (`client-001`)

```json
{
  "id": "client-001",
  "personal_details": {
    "first_name": "James",
    "last_name": "Whitfield",
    "date_of_birth": "1985-03-22",
    "email": "james.whitfield@email.co.uk",
    "phone": "07700 112233",
    "address": {
      "address_line_1": "14 Elm Grove",
      "address_line_2": "",
      "city": "Bristol",
      "postcode": "BS7 8TH",
      "country": "United Kingdom"
    }
  },
  "assets": [
    {
      "id": "asset-001",
      "type": "pension",
      "name": "Workplace Pension",
      "value": 87000,
      "currency": "GBP",
      "provider": "Scottish Widows"
    },
    {
      "id": "asset-002",
      "type": "savings",
      "name": "Emergency Fund",
      "value": 12000,
      "currency": "GBP",
      "provider": "Marcus by Goldman Sachs"
    }
  ],
  "liabilities": [
    {
      "id": "liability-001",
      "type": "mortgage",
      "provider": "Nationwide",
      "outstanding_balance": 195000,
      "currency": "GBP",
      "interest_rate_percent": 2.49,
      "end_date": "2036-09-01"
    }
  ],
  "income_items": [
    {
      "id": "income-001",
      "source": "employment",
      "amount": 52000,
      "currency": "GBP",
      "frequency": "annually"
    }
  ],
  "expense_items": [
    {
      "id": "expense-001",
      "category": "mortgage_payment",
      "amount": 870,
      "currency": "GBP",
      "frequency": "monthly"
    },
    {
      "id": "expense-002",
      "category": "childcare",
      "amount": 600,
      "currency": "GBP",
      "frequency": "monthly"
    }
  ]
}
```

---

## Scenario 2 — Margaret Chen (`client-002`)

```json
{
  "id": "client-002",
  "personal_details": {
    "first_name": "Margaret",
    "last_name": "Chen",
    "date_of_birth": "1962-11-08",
    "email": "margaret.chen@btinternet.com",
    "phone": "07412 339821",
    "address": {
      "address_line_1": "7 Willow Lane",
      "address_line_2": "Headingley",
      "city": "Leeds",
      "postcode": "LS6 3PA",
      "country": "United Kingdom"
    }
  },
  "assets": [
    {
      "id": "asset-001",
      "type": "pension",
      "name": "NHS Pension",
      "value": 310000,
      "currency": "GBP",
      "provider": "NHS Pensions"
    },
    {
      "id": "asset-002",
      "type": "pension",
      "name": "Private Pension",
      "value": 45000,
      "currency": "GBP",
      "provider": "Standard Life"
    },
    {
      "id": "asset-003",
      "type": "savings",
      "name": "Cash ISA",
      "value": 22000,
      "currency": "GBP",
      "provider": "Nationwide"
    },
    {
      "id": "asset-004",
      "type": "investment",
      "name": "Stocks and Shares ISA",
      "value": 38000,
      "currency": "GBP",
      "provider": "Hargreaves Lansdown"
    }
  ],
  "liabilities": [
    {
      "id": "liability-001",
      "type": "mortgage",
      "provider": "HSBC",
      "outstanding_balance": 64000,
      "currency": "GBP",
      "interest_rate_percent": 3.29,
      "end_date": "2031-04-01"
    },
    {
      "id": "liability-002",
      "type": "credit_card",
      "provider": "Barclaycard",
      "outstanding_balance": 3200,
      "currency": "GBP",
      "interest_rate_percent": 21.9,
      "limit": 5000
    }
  ],
  "income_items": [
    {
      "id": "income-001",
      "source": "employment",
      "amount": 48500,
      "currency": "GBP",
      "frequency": "annually"
    }
  ],
  "expense_items": [
    {
      "id": "expense-001",
      "category": "mortgage_payment",
      "amount": 520,
      "currency": "GBP",
      "frequency": "monthly"
    },
    {
      "id": "expense-002",
      "category": "credit_card_payment",
      "amount": 150,
      "currency": "GBP",
      "frequency": "monthly"
    },
    {
      "id": "expense-003",
      "category": "utilities",
      "amount": 210,
      "currency": "GBP",
      "frequency": "monthly"
    }
  ]
}
```
