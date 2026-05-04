from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from wealthai.config import LLM_RETRY_ATTEMPTS, LLM_RETRY_MAX_WAIT, LLM_RETRY_MIN_WAIT, MODEL
from wealthai.llm.state import AgentState
from wealthai.llm.validators import validate
from wealthai.schemas import ChangeLog, ClientProfile

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_PROMPT_TEMPLATE = "{version}_changelog.txt"


# ---------------------------------------------------------------------------
# LLM (singleton, constructed once per process)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _build_llm() -> Any:
    return ChatOllama(model=MODEL).with_structured_output(ChangeLog, method="json_mode")


# ---------------------------------------------------------------------------
# Retried LLM call
# ---------------------------------------------------------------------------


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(LLM_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=LLM_RETRY_MIN_WAIT, max=LLM_RETRY_MAX_WAIT),
    reraise=True,
)
async def _invoke_llm(system_prompt: str, transcript: str, profile: ClientProfile) -> ChangeLog:
    llm = _build_llm()
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=transcript)]
    result = await llm.ainvoke(messages)
    if not isinstance(result, ChangeLog):
        raise ValueError(f"LLM returned unexpected type: {type(result)}")
    validation = validate(result, profile)
    if not validation.valid:
        raise ValueError(f"ChangeLog failed validation: {validation.errors}")
    return result


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------


async def generate_changelog(state: AgentState) -> dict[str, Any]:
    """LangGraph node: produce a ChangeLog from a transcript and optional client profile."""
    prompt_path = _PROMPTS_DIR / _PROMPT_TEMPLATE.format(version=state.prompt_version)
    template = prompt_path.read_text()
    profile_json = json.dumps(state.client_profile.model_dump(mode="json"), indent=2)
    system_prompt = template.format(profile_json=profile_json)

    changelog = await _invoke_llm(system_prompt, state.transcript, state.client_profile)
    return {"changelog": changelog}
