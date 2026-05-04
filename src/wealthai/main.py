from __future__ import annotations

import asyncio

from wealthai.io import load_profile, load_transcript, store_changelog, store_profile
from wealthai.llm.merger import apply_changelog
from wealthai.llm.node import generate_changelog


async def _run(client_id: str) -> None:
    profile = load_profile(client_id)
    transcript = load_transcript(client_id)

    changelog = await generate_changelog(transcript, profile)
    print(changelog.model_dump_json(indent=2))

    store_changelog(client_id, changelog)
    store_profile(apply_changelog(profile, changelog))


def main(client_id: str) -> None:
    asyncio.run(_run(client_id))
