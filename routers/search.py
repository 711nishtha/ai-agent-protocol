"""
routers/search.py — GET /search
"""

from __future__ import annotations
from typing import List
from fastapi import APIRouter, Query, HTTPException

from database import get_connection
from models import AgentResponse
from routers.agents import _row_to_agent

router = APIRouter(tags=["Search"])


@router.get(
    "/search",
    response_model=List[AgentResponse],
    summary="Search agents by name or description",
)
def search_agents(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(50, ge=1, le=200),
) -> List[AgentResponse]:
    """
    Case-insensitive search across name, description, and tags.
    SQLite LIKE is used — no FTS5 extension required.
    """
    if not q.strip():
        raise HTTPException(status_code=422, detail="Query must not be blank.")

    term = f"%{q.strip().lower()}%"
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM agents
            WHERE  lower(name)        LIKE ?
               OR  lower(description) LIKE ?
               OR  lower(tags)        LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (term, term, term, limit),
        ).fetchall()
    return [_row_to_agent(r) for r in rows]
