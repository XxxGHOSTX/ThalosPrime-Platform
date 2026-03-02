"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.

Bootstrap script — run once from the repository root to materialise the
services/ingest module:

    python scripts/bootstrap_ingest.py

All generated files carry the mandatory IP header and are ruff-clean.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Canonical IP header embedded in every generated Python file
# ---------------------------------------------------------------------------
_HEADER = '''\
"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
'''

# ---------------------------------------------------------------------------
# File contents
# ---------------------------------------------------------------------------

_INIT = _HEADER  # bare package marker

_SCHEMA = (
    _HEADER
    + '''
import hashlib
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from core.utilities import now_iso


class IngestEvent(BaseModel):
    """Immutable, validated representation of a raw ingest event."""

    model_config = ConfigDict(frozen=True)

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    raw: str
    timestamp: str
    format: Literal["jsonl", "proxy_log", "http_push"]
    severity: Literal["INFO", "WARN", "ERROR", "CRITICAL"] = "INFO"
    metadata: dict = Field(default_factory=dict)


class NormalizedEvent(BaseModel):
    """Normalized event enriched with a deterministic input hash and normalization timestamp."""

    event_id: str
    source: str
    raw: str
    timestamp: str
    format: str
    severity: str
    metadata: dict
    normalized_at: str = Field(default_factory=now_iso)
    input_hash: str = ""

    @model_validator(mode="before")
    @classmethod
    def _auto_compute_input_hash(cls, data: Any) -> Any:
        """Auto-compute SHA-256 of the raw field when input_hash is not explicitly provided."""
        if isinstance(data, dict) and not data.get("input_hash") and "raw" in data:
            data["input_hash"] = hashlib.sha256(data["raw"].encode()).hexdigest()
        return data
'''
)

_NORMALIZER = (
    _HEADER
    + '''
import hashlib

from core.utilities import now_iso
from .schema import IngestEvent, NormalizedEvent


class EventNormalizer:
    """Transforms a raw IngestEvent into a NormalizedEvent with a deterministic hash and UTC timestamp."""

    def normalize(self, event: IngestEvent) -> NormalizedEvent:
        """
        Normalize an IngestEvent.

        Computes a SHA-256 digest of the raw payload and stamps the current UTC time
        as ``normalized_at``.  All original event fields are preserved verbatim.
        """
        input_hash = hashlib.sha256(event.raw.encode()).hexdigest()
        return NormalizedEvent(
            event_id=event.event_id,
            source=event.source,
            raw=event.raw,
            timestamp=event.timestamp,
            format=event.format,
            severity=event.severity,
            metadata=event.metadata,
            normalized_at=now_iso(),
            input_hash=input_hash,
        )
'''
)

_FILE_INGEST = (
    _HEADER
    + '''
import json
from pathlib import Path

from core.utilities import now_iso
from .schema import IngestEvent

# Top-level IngestEvent field names excluded when building per-event metadata from parsed JSON.
_KNOWN_FIELDS: frozenset[str] = frozenset(
    {"event_id", "source", "raw", "timestamp", "format", "severity", "metadata"}
)


class FileIngestor:
    """Ingests event data from local files in JSONL or proxy-log (plain-text) formats."""

    # ------------------------------------------------------------------
    # JSONL ingestion
    # ------------------------------------------------------------------

    def ingest_jsonl(self, path: str | Path) -> list[IngestEvent]:
        """
        Read a JSONL / NDJSON file and return one IngestEvent per non-blank line.

        Field-extraction rules:
        - ``source``    – value of the ``source`` key in the JSON object; defaults to ``"file"``.
        - ``raw``       – the full, unmodified text of the line.
        - ``timestamp`` – value of the ``timestamp`` key if present; otherwise ``now_iso()``.
        - ``severity``  – value of the ``severity`` key if present; otherwise ``"INFO"``.
        - ``metadata``  – all remaining JSON keys not in ``_KNOWN_FIELDS``.
        """
        path = Path(path)
        events: list[IngestEvent] = []
        with path.open("r", encoding="utf-8") as fh:
            for raw_line in fh:
                stripped = raw_line.strip()
                if not stripped:
                    continue
                data: dict = json.loads(stripped)
                source: str = data.get("source", "file")
                timestamp: str = data.get("timestamp", now_iso())
                severity: str = data.get("severity", "INFO")
                metadata: dict = {k: v for k, v in data.items() if k not in _KNOWN_FIELDS}
                events.append(
                    IngestEvent(
                        source=source,
                        raw=stripped,
                        timestamp=timestamp,
                        format="jsonl",
                        severity=severity,
                        metadata=metadata,
                    )
                )
        return events

    # ------------------------------------------------------------------
    # Proxy-log ingestion
    # ------------------------------------------------------------------

    def ingest_proxy_log(self, path: str | Path) -> list[IngestEvent]:
        """
        Read a plain-text proxy log (e.g. Apache combined, Squid) and return one
        IngestEvent per non-blank, non-comment line.

        Blank lines and lines whose first non-whitespace character is ``#`` are skipped.
        """
        path = Path(path)
        events: list[IngestEvent] = []
        with path.open("r", encoding="utf-8") as fh:
            for raw_line in fh:
                stripped = raw_line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                events.append(
                    IngestEvent(
                        source="proxy",
                        raw=stripped,
                        timestamp=now_iso(),
                        format="proxy_log",
                    )
                )
        return events

    # ------------------------------------------------------------------
    # Auto-detecting dispatcher
    # ------------------------------------------------------------------

    def ingest_file(self, path: str | Path) -> list[IngestEvent]:
        """
        Auto-detect the file format by extension and delegate to the appropriate ingestor.

        - ``*.jsonl`` / ``*.ndjson`` → :meth:`ingest_jsonl`
        - Anything else              → :meth:`ingest_proxy_log`
        """
        path = Path(path)
        if path.suffix in {".jsonl", ".ndjson"}:
            return self.ingest_jsonl(path)
        return self.ingest_proxy_log(path)
'''
)

_HTTP_INGEST = (
    _HEADER
    + '''
import hashlib
import hmac
import json
import os

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from core.utilities import now_iso
from .schema import IngestEvent

# IngestEvent field names excluded when extracting per-event metadata from raw HTTP payloads.
_KNOWN_FIELDS: frozenset[str] = frozenset(
    {"event_id", "source", "raw", "timestamp", "format", "severity", "metadata"}
)

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
'''
)

# ---------------------------------------------------------------------------
# Materialise the module
# ---------------------------------------------------------------------------

_FILES: dict[str, str] = {
    "__init__.py": _INIT,
    "schema.py": _SCHEMA,
    "normalizer.py": _NORMALIZER,
    "file_ingest.py": _FILE_INGEST,
    "http_ingest.py": _HTTP_INGEST,
}


def bootstrap(root: Path | None = None) -> None:
    """Create services/ingest/ and write all module files."""
    base = (root or Path(__file__).resolve().parent.parent) / "services" / "ingest"
    base.mkdir(parents=True, exist_ok=True)
    for filename, content in _FILES.items():
        target = base / filename
        if target.exists():
            print(f"  [skip]  {target}  (already exists)")
        else:
            target.write_text(content, encoding="utf-8")
            print(f"  [write] {target}")
    print(f"\nDone — {len(_FILES)} files written to {base}")


if __name__ == "__main__":
    bootstrap()
