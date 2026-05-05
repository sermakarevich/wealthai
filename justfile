default:
    just --list

install:
    uv sync --all-extras

run +client_ids:
    uv run run.py {{client_ids}}

run-all:
    uv run run.py client-001 client-002

evals +client_ids:
    uv run run_evals.py {{client_ids}}

evals-all:
    uv run run_evals.py client-001 client-002

# --- code quality ---

fmt:
    uv run ruff format src/ tests/ run.py run_evals.py

lint:
    uv run ruff check src/ tests/ run.py run_evals.py
    uv run mypy src/

fix:
    uv run ruff check --fix src/ tests/ run.py run_evals.py

# --- tests ---

test:
    uv run pytest -v

# --- ci ---

check: fmt lint test
