from __future__ import annotations

import asyncio
import logging

from wealthai.io import load_profile, load_transcript, store_changelog, store_profile
from wealthai.llm.merger import apply_changelog
from wealthai.llm.node import generate_changelog

logger = logging.getLogger(__name__)


async def _process(client_id: str) -> None:
    profile = load_profile(client_id)
    transcript = load_transcript(client_id)

    changelog = await generate_changelog(transcript, profile)
    logger.info(changelog.model_dump_json(indent=2))

    store_changelog(client_id, changelog)
    store_profile(apply_changelog(profile, changelog))


async def _run(client_ids: list[str]) -> None:
    await asyncio.gather(*(_process(cid) for cid in client_ids))


def main(client_ids: list[str]) -> None:
    asyncio.run(_run(client_ids))
