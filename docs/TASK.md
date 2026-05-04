# Fact Find Agent — Task Description

## 1. Context

Design and implement an AI agent that takes:
- a meeting transcript, and
- current facts we already have about a client

…and produces a change set that can be applied to the client record.

The change set must be expressed as:
1. New facts to create
2. Facts to update

Each change item must be auditable — meaning each suggested change should be justified with evidence from the transcript.

## 2. Requirements

- The agent must accept an input payload containing two required parts:
  - **Existing Client Information** (JSON schema defined in `INPUT_SCHEMA.md`, see `CLIENT_PROFILE.md` for examples)
  - **Meeting Transcript** (free text, see `TRANSCRIPT.md` for examples)

- Return JSON that contains **create** and **update** objects (JSON schema defined in `OUTPUT_SCHEMA.md`):
  - **create** object with information about new data (e.g., new pension provider or investment account)
  - **update** object that contains:
    - information that needs to be changed in the existing client profile (e.g., new address, changed income, changed mortgage payment)
    - updates must include old value and new value

- The application can be implemented as either:
  1. CLI that reads input JSON and prints output JSON, or
  2. Simple API endpoint: `POST /process_transcript_diff`

- Source code hosted in a repository (GitHub/Bitbucket/etc.) or provided as a zip file
- A README explaining how to run the agent locally
