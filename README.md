# WealthAI — Fact Find Agent

Extracts client profile changes from financial planning meeting transcripts using a local LLM.

## Setup

```bash
# Install Ollama: https://ollama.com
ollama pull gemma4:latest

uv sync --all-extras   # or: just install
```

## Usage

```bash
# Run the agent for a client
just run client-001

# Evaluate against expected output
just eval client-001

# Run tests / lint
just test
just lint
just check
```

Output files are written to `output/` with a datetime suffix:
- `output/changelogs/client-001_<datetime>.json` — the extracted changelog
- `output/clients/client-001_<datetime>.json` — the updated client profile

## Components

```
src/wealthai/
  schemas/        Pydantic models: ClientProfile, ChangeLog, Asset, Liability, ...
  llm/
    node.py       LangChain/Ollama node: prompts the LLM, retries, validates output
    merger.py     Applies a ChangeLog to a ClientProfile (pure, deterministic)
    validators/   Post-LLM sanity checks run before the changelog is applied.
                  `update_ids` rejects updates that reference IDs absent from the profile;
                  `create_sequence` checks that existing profile IDs form a gap-free sequence
                  so the merger can safely assign the next ID to each new record.
                  Validation failures trigger a retry via tenacity.
    prompts/      Versioned system prompt templates
  io/
    load.py       Reads client profile and transcript from input/
    store.py      Writes changelog and updated profile to output/ (datetime-versioned)
  evals.py        Precision / recall / F1 scoring against ground truth changelogs
  main.py         Pipeline: load → LLM → apply → store

run.py            CLI entry point — run the agent for a client ID
run_evals.py      CLI entry point — run evals against ground truth changelogs

input/
  clients/        Client profiles (JSON)
  transcripts/    Meeting transcripts (plain text)
  expected/       Ground truth changelogs for eval
```

## How it works

1. The agent reads a client profile and transcript.
2. A system prompt (with the current profile embedded as JSON) is sent to a local Ollama model.
3. The model returns a `ChangeLog`: a list of records to **create** and field values to **update**.
4. `merger.py` applies the changelog to the profile immutably, producing the updated state.
5. Both the changelog and updated profile are persisted to `output/`.

## Design simplifications

- **Read-only inputs:** The original client profile in `input/clients/` is never modified. Each run writes a new versioned snapshot to `output/clients/`, making it safe to run multiple experiments without corrupting the baseline.
- **Initial profile assumed pre-existing:** The first client profile is expected to already exist in `input/clients/`. Creating a profile from scratch is out of scope — the `ChangeLog` schema is designed for *incremental updates*, not initial population, so first-time onboarding should be handled by a separate flow.
- **Local model accuracy ceiling:** Results produced by a local Ollama model will fall meaningfully short of a cloud API model (e.g. Claude Sonnet/GPT-4o). Treat eval scores obtained with Ollama as a lower bound; production quality requires a frontier model.
