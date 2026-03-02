"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import hashlib
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from core.utilities import now_iso

# Field names of IngestEvent — used to separate known schema fields from metadata
# in JSONL and HTTP ingest parsing. Defined here so both ingestors share the same set.
INGEST_KNOWN_FIELDS: frozenset[str] = frozenset(
    {"event_id", "source", "raw", "timestamp", "format", "severity", "metadata"}
)


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
