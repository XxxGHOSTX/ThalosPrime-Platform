"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys
import argparse

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from .session_manager import ThalosSessionManager
from core.utilities import validate_seed
from services.ingest.http_ingest import router as ingest_router

app = FastAPI(
    title="Thalos Prime Control Plane",
    version="2.0.0",
    description="© 2026 Tony Ray Macier III. Sovereign deterministic control plane.",
)

app.include_router(ingest_router)

_session_manager = ThalosSessionManager()

# Prometheus metrics
_SESSIONS_CREATED = Counter(
    "thalos_sessions_created_total",
    "Total number of control-plane sessions created",
)
_TURNS_ADDED = Counter(
    "thalos_turns_added_total",
    "Total number of turns added to sessions",
)
_REQUEST_LATENCY = Histogram(
    "thalos_request_duration_seconds",
    "HTTP request latency in seconds",
    labelnames=["endpoint"],
)


class SessionRequest(BaseModel):
    context: dict = {}


class TurnRequest(BaseModel):
    role: str
    content: str


@app.get("/health")
def health() -> dict:
    """Liveness probe — returns service status."""
    return {
        "status": "ok",
        "service": "thalos-control-plane",
        "version": "2.0.0",
        "owner": "Tony Ray Macier III",
    }


@app.get("/metrics")
def metrics() -> Response:
    """Prometheus metrics scrape endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/sessions", status_code=201)
def create_session(request: SessionRequest) -> dict:
    """Create a new session and derive its deterministic execution seed."""
    with _REQUEST_LATENCY.labels(endpoint="/sessions").time():
        session_id = _session_manager.create_session(context=request.context)
        session = _session_manager.get_session(session_id)
        _SESSIONS_CREATED.inc()
        return {"session_id": session_id, "seed": session["seed"]}


@app.post("/sessions/{session_id}/turns")
def add_turn(session_id: str, request: TurnRequest) -> dict:
    """Append a conversation turn to an existing session."""
    try:
        with _REQUEST_LATENCY.labels(endpoint="/sessions/turns").time():
            state_hash = _session_manager.add_turn(session_id, request.role, request.content)
            _TURNS_ADDED.inc()
            return {"state_hash": state_hash, "session_id": session_id}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


@app.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict:
    """Retrieve the full session state including all turns."""
    session = _session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session


def main() -> None:
    parser = argparse.ArgumentParser(description="Thalos Prime Control Plane API")
    parser.add_argument("--seed", type=int, required=True, help="64-bit execution seed (required)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    try:
        validate_seed(args.seed)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
