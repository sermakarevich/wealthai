from __future__ import annotations

import asyncio

from wealthai.io import load_profile, load_transcript, store_changelog, store_profile
from wealthai.llm.merger import apply_changelog
from wealthai.llm.node import generate_changelog
from wealthai.llm.state import AgentState


async def _run(client_id: str) -> None:
    profile = load_profile(client_id)
    transcript = load_transcript(client_id)
    state = AgentState(transcript=transcript, client_profile=profile)

    result = await generate_changelog(state)
    changelog = result["changelog"]
    print(changelog.model_dump_json(indent=2))

    merged = apply_changelog(profile, changelog)

    store_changelog(client_id, changelog)
    store_profile(merged)


def main(client_id: str) -> None:
    asyncio.run(_run(client_id))
