"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import argparse
import hmac
import json
import os
import sys

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .session_manager import ThalosSessionManager
from core.utilities import validate_seed

app = FastAPI(
    title="Thalos Prime Control Plane",
    version="2.0.0",
    description="© 2026 Tony Ray Macier III. Sovereign deterministic control plane.",
)

_session_manager = ThalosSessionManager()


def _configured_api_tokens() -> dict[str, str]:
    """Load identity-to-token credentials; invalid or weak configuration fails closed."""
    raw = os.environ.get("THALOS_CONTROL_PLANE_API_TOKENS", "")
    try:
        tokens = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}
    if not isinstance(tokens, dict) or not tokens:
        return {}
    if any(
        not isinstance(subject, str)
        or not subject.strip()
        or not isinstance(token, str)
        or len(token.encode("utf-8")) < 32
        for subject, token in tokens.items()
    ):
        return {}
    if len(set(tokens.values())) != len(tokens):
        return {}
    return tokens


def require_api_identity(authorization: str | None = Header(default=None)) -> str:
    """Authenticate a configured bearer token and return its principal identity."""
    tokens = _configured_api_tokens()
    if not tokens:
        raise HTTPException(
            status_code=503,
            detail="Control-plane authentication is not configured with valid unique tokens",
        )
    if not authorization:
        raise HTTPException(status_code=401, detail="Bearer token required")
    scheme, _, supplied = authorization.partition(" ")
    if scheme.lower() != "bearer" or not supplied.strip():
        raise HTTPException(status_code=401, detail="Bearer token required")
    supplied = supplied.strip()
    identity = None
    for subject, expected in tokens.items():
        if hmac.compare_digest(supplied, expected):
            identity = subject
    if identity is None:
        raise HTTPException(status_code=401, detail="Invalid bearer token")
    return identity


class SessionRequest(BaseModel):
    context: dict = Field(default_factory=dict)


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


@app.post("/sessions", status_code=201)
def create_session(
    request: SessionRequest,
    identity: str = Depends(require_api_identity),
) -> dict:
    """Create a new session owned by the authenticated principal."""
    session_id = _session_manager.create_session(context=request.context, owner_id=identity)
    session = _session_manager.get_session(session_id, owner_id=identity)
    return {"session_id": session_id, "seed": session["seed"]}


@app.post("/sessions/{session_id}/turns")
def add_turn(
    session_id: str,
    request: TurnRequest,
    identity: str = Depends(require_api_identity),
) -> dict:
    """Append a conversation turn to a session owned by the authenticated principal."""
    try:
        state_hash = _session_manager.add_turn(
            session_id, request.role, request.content, owner_id=identity
        )
        return {"state_hash": state_hash, "session_id": session_id}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


@app.get("/sessions/{session_id}")
def get_session(
    session_id: str,
    identity: str = Depends(require_api_identity),
) -> dict:
    """Retrieve session state only when the authenticated principal owns it."""
    session = _session_manager.get_session(session_id, owner_id=identity)
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
