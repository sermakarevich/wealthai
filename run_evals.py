from __future__ import annotations

import argparse

from wealthai.evals import run_eval


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run evals against expected changelogs")
    parser.add_argument("client_ids", nargs="+", help='e.g. "client-001 client-002"')
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    for client_id in args.client_ids:
        run_eval(client_id)
