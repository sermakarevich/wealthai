default:
    just --list

install:
    uv sync --all-extras

run client_id:
    uv run run.py {{client_id}}

eval +client_ids:
    uv run run_evals.py {{client_ids}}

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
