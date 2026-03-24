# Autonomous AI Agent Protocol

A production-quality FastAPI backend for registering AI agents, discovering
them via search, and logging + aggregating inter-agent usage.

## Tech Stack
- Python 3.11+, FastAPI 0.115, Pydantic v2, SQLite (WAL mode)

## Project Structure
```
  ai_agent_protocol/
  ├── main.py              FastAPI app + error handlers
  ├── database.py          SQLite connection + schema init
  ├── models.py            Pydantic schemas
  ├── routers/
  │   ├── agents.py        POST /agents, GET /agents
  │   ├── search.py        GET /search
  │   └── usage.py         POST /usage, GET /usage-summary
  └── utils/
      └── keyword_extractor.py  Tag extraction (no LLM)
```
## Quickstart
```
  python3 -m venv venv && source venv/bin/activate
  pip install -r requirements.txt
  uvicorn main:app --reload --port 8000
  open http://localhost:8000/docs
```
## API Endpoints
```
  POST /agents          Register a new agent
  GET  /agents          List all agents
  GET  /search?q=...    Case-insensitive search
  POST /usage           Log inter-agent usage (idempotent via request_id)
  GET  /usage-summary   Aggregated units/calls per agent
```
## Key Design Decisions
  - SQLite chosen for zero-dependency local setup (swap for Postgres at scale).
  - Idempotency: request_id UNIQUE constraint prevents double-charging.
  - Tag extraction: pure Python bigram + frequency ranking, no LLM needed.
  - WAL mode: allows concurrent reads without blocking writes.
  - Error handling: custom 422 formatter, catch-all 500 handler.
