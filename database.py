"""
database.py — SQLite setup via sqlite3 (no ORM, clean and lightweight).
Creates tables on first run. All connections use WAL mode for concurrency.
"""

import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "agents.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # dict-like row access
    conn.execute("PRAGMA journal_mode=WAL")  # safe concurrent reads
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they do not exist. Idempotent — safe to call every startup."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL UNIQUE,
                description TEXT    NOT NULL,
                endpoint    TEXT    NOT NULL,
                tags        TEXT    NOT NULL DEFAULT '',
                created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id  TEXT    NOT NULL UNIQUE,
                caller      TEXT    NOT NULL,
                target      TEXT    NOT NULL,
                units       INTEGER NOT NULL,
                logged_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_usage_caller ON usage_logs(caller)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_usage_target ON usage_logs(target)"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_name  ON agents(name)")
        conn.commit()
