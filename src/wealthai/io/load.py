from __future__ import annotations

from pathlib import Path

from wealthai.schemas import ChangeLog, ClientProfile

_PROJECT_ROOT = Path(__file__).parents[3]
_INPUT_DIR = _PROJECT_ROOT / "input"

_CLIENT_TEMPLATE = "clients/{id}.json"
_TRANSCRIPT_TEMPLATE = "transcripts/{id}.txt"


def load_profile(client_id: str, base_dir: Path | None = None) -> ClientProfile:
    root = base_dir if base_dir is not None else _INPUT_DIR
    path = root / _CLIENT_TEMPLATE.format(id=client_id)
    return ClientProfile.model_validate_json(path.read_text())


def load_transcript(client_id: str, base_dir: Path | None = None) -> str:
    root = base_dir if base_dir is not None else _INPUT_DIR
    path = root / _TRANSCRIPT_TEMPLATE.format(id=client_id)
    return path.read_text()


def load_changelog(client_id: str, base_dir: Path | None = None) -> ChangeLog:
    root = base_dir if base_dir is not None else _PROJECT_ROOT / "output"
    candidates = sorted((root / "changelogs").glob(f"{client_id}_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No stored changelog found for {client_id!r}")
    return ChangeLog.model_validate_json(candidates[-1].read_text())
