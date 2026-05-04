# Output Schema — Fact Find Agent

The agent must return JSON conforming to this schema, containing `create` and `update` objects.
Every item must include an `evidence` field quoting the relevant passage from the transcript.

```json
{
  "$schema": "https://json-schema.org/draft-07/schema",
  "title": "Fact Find Agent Output Schema",
  "type": "object",
  "properties": {
    "create": {
      "type": "object",
      "properties": {
        "assets": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": { "type": "string" },
              "name": { "type": "string" },
              "value": { "type": "number" },
              "currency": { "type": "string" },
              "provider": { "type": "string" },
              "evidence": { "type": "string" }
            }
          }
        },
        "liabilities": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": { "type": "string" },
              "provider": { "type": "string" },
              "outstanding_balance": { "type": "number" },
              "currency": { "type": "string" },
              "interest_rate_percent": { "type": "number" },
              "evidence": { "type": "string" }
            }
          }
        },
        "income_items": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "source": { "type": "string" },
              "amount": { "type": "number" },
              "currency": { "type": "string" },
              "frequency": { "type": "string" },
              "evidence": { "type": "string" }
            }
          }
        },
        "expense_items": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "category": { "type": "string" },
              "amount": { "type": "number" },
              "currency": { "type": "string" },
              "frequency": { "type": "string" },
              "evidence": { "type": "string" }
            }
          }
        }
      }
    },
    "update": {
      "type": "object",
      "properties": {
        "personal_details": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "field": { "type": "string" },
              "old_value": {},
              "new_value": {},
              "evidence": { "type": "string" }
            }
          }
        },
        "assets": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": { "type": "string" },
              "field": { "type": "string" },
              "old_value": {},
              "new_value": {},
              "evidence": { "type": "string" }
            }
          }
        },
        "liabilities": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": { "type": "string" },
              "field": { "type": "string" },
              "old_value": {},
              "new_value": {},
              "evidence": { "type": "string" }
            }
          }
        },
        "income_items": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": { "type": "string" },
              "field": { "type": "string" },
              "old_value": {},
              "new_value": {},
              "evidence": { "type": "string" }
            }
          }
        },
        "expense_items": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": { "type": "string" },
              "field": { "type": "string" },
              "old_value": {},
              "new_value": {},
              "evidence": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```
