from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from pydantic import ValidationError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from wealthai.config import LLM_RETRY_ATTEMPTS, LLM_RETRY_MAX_WAIT, LLM_RETRY_MIN_WAIT, MODEL, PROMPT_VERSION
from wealthai.llm.validators import validate
from wealthai.schemas import ChangeLog, ClientProfile


class ChangeLogValidationError(Exception):
    """LLM returned a structurally valid ChangeLog that failed semantic validation."""


_PROMPTS_DIR = Path(__file__).parent / "prompts"


@lru_cache(maxsize=1)
def _build_llm() -> Any:
    return ChatOllama(model=MODEL).with_structured_output(ChangeLog, method="json_mode")


@retry(
    retry=retry_if_exception_type((ValidationError, ChangeLogValidationError)),
    stop=stop_after_attempt(LLM_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=LLM_RETRY_MIN_WAIT, max=LLM_RETRY_MAX_WAIT),
    reraise=True,
)
async def _invoke_llm(system_prompt: str, transcript: str, profile: ClientProfile) -> ChangeLog:
    llm = _build_llm()
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=transcript)]
    result = await llm.ainvoke(messages)
    if not isinstance(result, ChangeLog):
        raise ChangeLogValidationError(f"LLM returned unexpected type: {type(result)}")
    validation = validate(result, profile)
    if not validation.valid:
        raise ChangeLogValidationError(f"ChangeLog failed validation: {validation.errors}")
    return result


async def generate_changelog(transcript: str, profile: ClientProfile) -> ChangeLog:
    prompt_path = _PROMPTS_DIR / f"{PROMPT_VERSION}_changelog.txt"
    template = prompt_path.read_text()
    profile_json = json.dumps(profile.model_dump(mode="json"), indent=2)
    schema_json = json.dumps(ChangeLog.model_json_schema(), indent=2)
    system_prompt = template.format(profile_json=profile_json, schema_json=schema_json)
    return await _invoke_llm(system_prompt, transcript, profile)
