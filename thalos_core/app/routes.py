"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from thalos_core.audit.logger import log_event
from thalos_core.app.validator import validate_startup
from thalos_core.engine.mnn import run_mnn
from thalos_core.engine.state import get_state, update_state
from thalos_core.metrics.engine import (
    get_metrics_snapshot,
    inc_ingestion_events,
    inc_ingestion_failures,
    render_prometheus_metrics,
    set_sieve_score,
)

router = APIRouter()

_APP_SEED: int = 0


def set_app_seed(seed: int) -> None:
    global _APP_SEED
    _APP_SEED = seed


def get_app_seed() -> int:
    return _APP_SEED


class QueryRequest(BaseModel):
    query: str


@router.get("/")
def root() -> dict:
    return {"service": "thalos-core", "version": "1.0.0", "seed_mode": "enforced"}


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict:
    try:
        validate_startup()
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/query")
def handle_query(request: QueryRequest) -> dict:
    seed = get_app_seed()
    try:
        state = get_state()
        result = run_mnn(seed, request.query, state)
        inc_ingestion_events()
        set_sieve_score(result["sieve_score"])
        update_state(
            {
                "last_query": request.query,
                "last_seed": seed,
                "last_hash": result["hash"],
                "thalos_sieve_score": result["sieve_score"],
                "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
            }
        )
        metrics = get_metrics_snapshot()
        log_event(seed, request.query, result["hash"], result["hash"], metrics)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        inc_ingestion_failures()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    return PlainTextResponse(render_prometheus_metrics(), media_type="text/plain; version=0.0.4")
