from __future__ import annotations

import logging
import sys

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"


def configure(level: int = logging.INFO) -> None:
    """One-time logging setup for CLI entry points. Idempotent (uses force=True)."""
    logging.basicConfig(
        level=level,
        format=_FORMAT,
        datefmt=_DATEFMT,
        stream=sys.stdout,
        force=True,
    )
