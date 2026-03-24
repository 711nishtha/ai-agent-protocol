"""
routers/agents.py — POST /agents, GET /agents
"""

from __future__ import annotations
from typing import List
from fastapi import APIRouter, HTTPException, Query, status
import sqlite3

from database import get_connection
from models import AgentCreate, AgentResponse
from utils.keyword_extractor import extract_tags


router = APIRouter(prefix="/agents", tags=["Agents"])


def _row_to_agent(row) -> AgentResponse:
    tags = [t.strip() for t in row["tags"].split(",") if t.strip()]
    return AgentResponse(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        endpoint=row["endpoint"],
        tags=tags,
        created_at=row["created_at"],
    )


@router.post(
    "",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new agent",
)
def create_agent(payload: AgentCreate) -> AgentResponse:
    tags_str = ",".join(extract_tags(payload.description))
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO agents (name, description, endpoint, tags) VALUES (?, ?, ?, ?)",
                (payload.name, payload.description, payload.endpoint, tags_str),
            )
            conn.commit()
            agent_id = cursor.lastrowid
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM agents WHERE id = ?", (agent_id,)
            ).fetchone()
        return _row_to_agent(row)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An agent with the name '{payload.name}' already exists.",
        )


@router.get(
    "", response_model=List[AgentResponse], summary="List all registered agents"
)
def list_agents(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> List[AgentResponse]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM agents ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [_row_to_agent(r) for r in rows]
