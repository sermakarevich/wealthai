from __future__ import annotations

import argparse

from wealthai.logging import configure


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run evals against expected changelogs")
    parser.add_argument("client_ids", nargs="+", help='e.g. "client-001 client-002"')
    return parser.parse_args()


if __name__ == "__main__":
    configure()

    from wealthai.evals import run_evals

    args = _parse_args()
    for client_id in args.client_ids:
        run_evals(client_id)
