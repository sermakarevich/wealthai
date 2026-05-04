# Input Schema — Client Profile

The input payload to the agent must include the existing client profile conforming to this JSON schema.

```json
{
  "$schema": "https://json-schema.org/draft-07/schema",
  "title": "Client profile",
  "type": "object",
  "properties": {
    "id": {
      "type": "string"
    },
    "personal_details": {
      "type": "object",
      "properties": {
        "first_name": { "type": "string" },
        "last_name": { "type": "string" },
        "date_of_birth": { "type": "string", "format": "date" },
        "email": { "type": "string", "format": "email" },
        "phone": { "type": "string" },
        "address": {
          "type": "object",
          "properties": {
            "address_line_1": { "type": "string" },
            "address_line_2": { "type": "string" },
            "city": { "type": "string" },
            "postcode": { "type": "string" },
            "country": { "type": "string" }
          }
        }
      }
    },
    "assets": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "type": { "type": "string" },
          "name": { "type": "string" },
          "value": { "type": "number" },
          "currency": { "type": "string" },
          "provider": { "type": "string" }
        }
      }
    },
    "liabilities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "type": { "type": "string" },
          "provider": { "type": "string" },
          "outstanding_balance": { "type": "number" },
          "currency": { "type": "string" },
          "interest_rate_percent": { "type": "number" },
          "end_date": { "type": "string", "format": "date" },
          "limit": { "type": "number" }
        }
      }
    },
    "income_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "source": { "type": "string" },
          "amount": { "type": "number" },
          "currency": { "type": "string" },
          "frequency": {
            "type": "string",
            "enum": ["weekly", "monthly", "annually"]
          }
        }
      }
    },
    "expense_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "category": { "type": "string" },
          "currency": { "type": "string" },
          "amount": { "type": "number" },
          "frequency": {
            "type": "string",
            "enum": ["weekly", "monthly", "annually"]
          }
        }
      }
    }
  }
}
```
