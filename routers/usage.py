"""
routers/usage.py — POST /usage, GET /usage-summary

Idempotency guarantee:
    request_id has a UNIQUE constraint in SQLite.
    Duplicate request_id -> return original record with duplicate=True.
    No double-write, no error to the caller.
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException, status
import sqlite3

from database import get_connection
from models import (
    UsageCreate,
    UsageLogResponse,
    AgentUsageSummary,
    UsageSummaryResponse,
)

router = APIRouter(tags=["Usage"])


@router.post(
    "/usage",
    response_model=UsageLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log inter-agent usage",
)
def log_usage(payload: UsageCreate) -> UsageLogResponse:
    # Validate target agent exists
    with get_connection() as conn:
        target_exists = conn.execute(
            "SELECT 1 FROM agents WHERE name = ?", (payload.target,)
        ).fetchone()
    if not target_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target agent '{payload.target}' is not registered.",
        )

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO usage_logs (request_id, caller, target, units) VALUES (?, ?, ?, ?)",
                (payload.request_id, payload.caller, payload.target, payload.units),
            )
            conn.commit()
            log_id = cursor.lastrowid
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM usage_logs WHERE id = ?", (log_id,)
            ).fetchone()
        return UsageLogResponse(**dict(row), duplicate=False)

    except sqlite3.IntegrityError:
        # Duplicate request_id — idempotent replay
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM usage_logs WHERE request_id = ?", (payload.request_id,)
            ).fetchone()
        return UsageLogResponse(**dict(row), duplicate=True)


@router.get(
    "/usage-summary",
    response_model=UsageSummaryResponse,
    summary="Aggregated usage statistics per agent",
)
def usage_summary() -> UsageSummaryResponse:
    with get_connection() as conn:
        received = conn.execute(
            "SELECT target, SUM(units) total_units, COUNT(*) total_calls FROM usage_logs GROUP BY target"
        ).fetchall()
        sent = conn.execute(
            "SELECT caller, SUM(units) total_units, COUNT(*) total_calls FROM usage_logs GROUP BY caller"
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM usage_logs").fetchone()[0]

    stats: dict = {}
    for r in received:
        stats.setdefault(r["target"], {"ru": 0, "rc": 0, "su": 0, "sc": 0})
        stats[r["target"]]["ru"] = r["total_units"]
        stats[r["target"]]["rc"] = r["total_calls"]
    for r in sent:
        stats.setdefault(r["caller"], {"ru": 0, "rc": 0, "su": 0, "sc": 0})
        stats[r["caller"]]["su"] = r["total_units"]
        stats[r["caller"]]["sc"] = r["total_calls"]

    return UsageSummaryResponse(
        agents=[
            AgentUsageSummary(
                agent_name=name,
                total_units_received=v["ru"],
                total_calls_received=v["rc"],
                total_units_sent=v["su"],
                total_calls_sent=v["sc"],
            )
            for name, v in sorted(stats.items())
        ],
        total_log_entries=total,
    )
