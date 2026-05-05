from __future__ import annotations

import argparse

from wealthai.logging import configure


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fact Find Agent — produce a ChangeLog from a transcript")
    parser.add_argument("client_ids", nargs="+", help='e.g. "client-001 client-002"')
    return parser.parse_args()


if __name__ == "__main__":
    configure()

    from wealthai.main import main

    args = _parse_args()
    main(args.client_ids)
