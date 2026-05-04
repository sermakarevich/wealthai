from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from wealthai.schemas import ChangeLog, ClientProfile

_PROJECT_ROOT = Path(__file__).parents[3]
_OUTPUT_DIR = _PROJECT_ROOT / "output"

_CHANGELOG_TEMPLATE = "changelogs/{id}_{dt}.json"
_CLIENT_TEMPLATE = "clients/{id}_{dt}.json"


def _now() -> str:
    return datetime.now().strftime("%Y%m%dT%H%M%S")


def store_changelog(client_id: str, changelog: ChangeLog, base_dir: Path | None = None) -> None:
    root = base_dir if base_dir is not None else _OUTPUT_DIR
    path = root / _CHANGELOG_TEMPLATE.format(id=client_id, dt=_now())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(changelog.model_dump_json(indent=2))


def store_profile(profile: ClientProfile, base_dir: Path | None = None) -> None:
    root = base_dir if base_dir is not None else _OUTPUT_DIR
    path = root / _CLIENT_TEMPLATE.format(id=profile.id, dt=_now())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile.model_dump(mode="json"), indent=2))
