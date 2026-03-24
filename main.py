"""
main.py — FastAPI entry point

Run with:
    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from database import init_db
from routers import agents, search, usage


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # creates tables on first run
    yield


app = FastAPI(
    title="Autonomous AI Agent Protocol",
    description="Mini Agent Discovery + Usage platform.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({"field": field or "body", "message": error["msg"]})
    return JSONResponse(
        status_code=422, content={"detail": "Validation failed", "errors": errors}
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(agents.router)
app.include_router(search.router)
app.include_router(usage.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Visit /docs for interactive API reference."}
