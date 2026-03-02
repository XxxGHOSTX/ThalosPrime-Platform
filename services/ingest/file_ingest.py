"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import json
from pathlib import Path

from core.utilities import now_iso
from .schema import IngestEvent

# Top-level IngestEvent field names excluded when building per-event metadata from parsed JSON.
_KNOWN_FIELDS: frozenset[str] = frozenset({"event_id", "source", "raw", "timestamp", "format", "severity", "metadata"})


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
