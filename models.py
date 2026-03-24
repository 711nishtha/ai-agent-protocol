"""
models.py — Pydantic v2 request / response schemas.
Single source of truth for all data shapes.
"""

from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field, field_validator
import re


# ── Agent ─────────────────────────────────────────────────────────────


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    endpoint: str = Field(...)

    @field_validator("name")
    @classmethod
    def name_no_special(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[\w\-. ]+$", v):
            raise ValueError(
                "Agent name may only contain letters, digits, spaces, hyphens, dots, underscores."
            )
        return v

    @field_validator("endpoint")
    @classmethod
    def endpoint_must_be_url(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^https?://", v, re.IGNORECASE):
            raise ValueError("endpoint must start with http:// or https://")
        return v


class AgentResponse(BaseModel):
    id: int
    name: str
    description: str
    endpoint: str
    tags: List[str]
    created_at: str


# ── Usage ─────────────────────────────────────────────────────────────


class UsageCreate(BaseModel):
    caller: str = Field(..., min_length=1, max_length=100)
    target: str = Field(..., min_length=1, max_length=100)
    units: int = Field(..., gt=0, le=1_000_000)
    request_id: str = Field(..., min_length=1, max_length=200)

    @field_validator("caller", "target", "request_id")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class UsageLogResponse(BaseModel):
    id: int
    request_id: str
    caller: str
    target: str
    units: int
    logged_at: str
    duplicate: bool = False  # True when idempotency replay occurred


class AgentUsageSummary(BaseModel):
    agent_name: str
    total_units_received: int
    total_calls_received: int
    total_units_sent: int
    total_calls_sent: int


class UsageSummaryResponse(BaseModel):
    agents: List[AgentUsageSummary]
    total_log_entries: int
