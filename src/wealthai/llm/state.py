from __future__ import annotations

from pydantic import BaseModel

from wealthai.schemas import ChangeLog, ClientProfile


class AgentState(BaseModel):
    transcript: str
    client_profile: ClientProfile
    prompt_version: str = "v1"
    changelog: ChangeLog | None = None
    error: str | None = None
