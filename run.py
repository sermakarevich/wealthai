from __future__ import annotations

import argparse

from wealthai.main import main


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fact Find Agent — produce a ChangeLog from a transcript")
    parser.add_argument("client_id", help='Client ID matching an input file, e.g. "client-001"')
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    main(args.client_id)
