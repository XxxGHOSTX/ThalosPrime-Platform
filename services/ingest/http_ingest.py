"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import hashlib
import hmac
import json
import os

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from core.utilities import now_iso
from .schema import IngestEvent

# IngestEvent field names excluded when extracting per-event metadata from raw HTTP payloads.
_KNOWN_FIELDS: frozenset[str] = frozenset({"event_id", "source", "raw", "timestamp", "format", "severity", "metadata"})

router = APIRouter(prefix="/ingest", tags=["ingest"])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class IngestEventRequest(BaseModel):
    """Payload accepted by the HTTP ingest endpoint."""

    events: list[dict]
    source: str = "http_push"


# ---------------------------------------------------------------------------
# Security dependency
# ---------------------------------------------------------------------------


def verify_api_token(x_api_token: str = Header(...)) -> None:
    """
    FastAPI dependency that validates the ``X-Api-Token`` request header.

    The expected token is read from the ``THALOS_API_TOKEN`` environment variable
    (default: ``"thalos-dev-token"``).  Comparison is performed with
    :func:`hmac.compare_digest` to prevent timing-based side-channel attacks.
    Raises :class:`~fastapi.HTTPException` 401 on mismatch.
    """
    expected: str = os.environ.get("THALOS_API_TOKEN", "thalos-dev-token")
    if not hmac.compare_digest(x_api_token, expected):
        raise HTTPException(status_code=401, detail="Invalid API token")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/events")
async def post_ingest_events(
    request: IngestEventRequest,
    _: None = Depends(verify_api_token),
) -> dict:
    """
    Accept a batch of raw event dicts over HTTP, coerce them into :class:`~.schema.IngestEvent`
    objects, and return a summary payload.

    Response fields:
    - ``accepted``   – number of events successfully ingested.
    - ``event_ids``  – list of auto-generated UUIDs for each accepted event.
    - ``input_hash`` – SHA-256 of the concatenated ``raw`` strings for the entire batch.
    """
    ingested: list[IngestEvent] = []

    for event_dict in request.events:
        raw_payload: str = json.dumps(event_dict)
        timestamp: str = event_dict.get("timestamp", now_iso())
        severity: str = event_dict.get("severity", "INFO")
        metadata: dict = {k: v for k, v in event_dict.items() if k not in _KNOWN_FIELDS}

        event = IngestEvent(
            source=request.source,
            raw=raw_payload,
            timestamp=timestamp,
            format="http_push",
            severity=severity,
            metadata=metadata,
        )
        ingested.append(event)

    combined_raw: str = "".join(e.raw for e in ingested)
    input_hash: str = hashlib.sha256(combined_raw.encode()).hexdigest()

    return {
        "accepted": len(ingested),
        "event_ids": [e.event_id for e in ingested],
        "input_hash": input_hash,
    }
