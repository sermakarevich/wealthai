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
# Run the agent for all clients
just run-all

# Evaluate against expected output for all clients
just evals-all

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
    node.py       Prompts the LLM, validates output, retries on failure
    merger.py     Applies a ChangeLog to a ClientProfile (pure, deterministic)
    validators/   Post-LLM validators (see How it works)
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
  expected/       Ground truth changelogs for evals
```

## How it works

1. The agent reads a client profile and transcript.
2. A system prompt (with the current profile and output schema embedded as JSON) is sent to a local Ollama model.
3. The model returns a `ChangeLog`: a list of records to **create** and field values to **update**. Every item carries an `evidence` field quoting the transcript passage that supports the change.
4. A chain of validators runs against the changelog before it is accepted. Each validator is an independent, composable check — new ones can be added to `llm/validators/` without touching the rest of the pipeline. Any failure triggers a retry (up to 3 attempts via tenacity).
5. `merger.py` applies the changelog to the profile immutably, producing the updated state.
6. Both the changelog and updated profile are persisted to `output/`.

## Design simplifications

- **Read-only inputs:** The original client profile in `input/clients/` is never modified. Each run writes a new versioned snapshot to `output/clients/`, making it safe to run multiple experiments without corrupting the baseline.
- **Initial profile assumed pre-existing:** The first client profile is expected to already exist in `input/clients/`. Creating a profile from scratch is out of scope — the `ChangeLog` schema is designed for *incremental updates*, not initial population, so first-time onboarding should be handled by a separate flow.
- **Local model accuracy ceiling:** Results produced by a local Ollama model will fall meaningfully short of a cloud API model (e.g. Claude Sonnet/GPT). Treat evals scores obtained with Ollama as a lower bound and a codebase test; production quality requires a frontier model.
