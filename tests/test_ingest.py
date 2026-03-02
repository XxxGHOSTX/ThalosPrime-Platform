"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys
import json
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ingest.schema import IngestEvent, NormalizedEvent  # noqa: E402
from services.ingest.normalizer import EventNormalizer  # noqa: E402
from services.ingest.file_ingest import FileIngestor  # noqa: E402


# ──────────────────────────────────────────────────────────────────────────────
# Schema tests
# ──────────────────────────────────────────────────────────────────────────────


def test_ingest_event_auto_generates_event_id():
    event = IngestEvent(source="test", raw="line", timestamp="2026-01-01T00:00:00Z", format="proxy_log")
    assert event.event_id
    assert len(event.event_id) == 36  # UUID4 format


def test_ingest_event_defaults():
    event = IngestEvent(source="test", raw="line", timestamp="2026-01-01T00:00:00Z", format="jsonl")
    assert event.severity == "INFO"
    assert event.metadata == {}


def test_ingest_event_is_frozen():
    event = IngestEvent(source="test", raw="line", timestamp="2026-01-01T00:00:00Z", format="proxy_log")
    with pytest.raises((TypeError, Exception)):
        event.source = "other"  # type: ignore[misc]


def test_normalized_event_has_input_hash():
    ne = NormalizedEvent(
        event_id="abc",
        source="test",
        raw="hello",
        timestamp="2026-01-01T00:00:00Z",
        format="proxy_log",
        severity="INFO",
        metadata={},
    )
    assert ne.input_hash
    assert len(ne.input_hash) == 64  # SHA-256 hex digest


def test_normalized_event_input_hash_deterministic():
    args = dict(
        event_id="abc",
        source="test",
        raw="hello",
        timestamp="2026-01-01T00:00:00Z",
        format="proxy_log",
        severity="INFO",
        metadata={},
    )
    ne1 = NormalizedEvent(**args)
    ne2 = NormalizedEvent(**args)
    assert ne1.input_hash == ne2.input_hash


# ──────────────────────────────────────────────────────────────────────────────
# Normalizer tests
# ──────────────────────────────────────────────────────────────────────────────


def test_normalizer_produces_normalized_event():
    import hashlib

    event = IngestEvent(source="test", raw="raw_data", timestamp="2026-01-01T00:00:00Z", format="proxy_log")
    normalizer = EventNormalizer()
    result = normalizer.normalize(event)
    assert isinstance(result, NormalizedEvent)
    assert result.event_id == event.event_id
    assert result.source == event.source
    assert result.raw == event.raw
    expected_hash = hashlib.sha256("raw_data".encode()).hexdigest()
    assert result.input_hash == expected_hash


def test_normalizer_input_hash_matches_sha256():
    import hashlib

    event = IngestEvent(source="test", raw="my raw data", timestamp="2026-01-01T00:00:00Z", format="proxy_log")
    normalizer = EventNormalizer()
    result = normalizer.normalize(event)
    expected = hashlib.sha256("my raw data".encode()).hexdigest()
    assert result.input_hash == expected


# ──────────────────────────────────────────────────────────────────────────────
# File ingest tests
# ──────────────────────────────────────────────────────────────────────────────


def test_ingest_jsonl_basic():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps({"source": "net", "raw": "line1", "timestamp": "2026-01-01T00:00:00Z"}) + "\n")
        f.write(json.dumps({"source": "net", "raw": "line2", "timestamp": "2026-01-01T00:00:00Z"}) + "\n")
        path = f.name
    try:
        ingestor = FileIngestor()
        events = ingestor.ingest_jsonl(path)
        assert len(events) == 2
        assert events[0].format == "jsonl"
        assert events[0].source == "net"
    finally:
        Path(path).unlink()


def test_ingest_jsonl_skips_blank_lines():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write("\n")
        f.write(json.dumps({"source": "net", "raw": "line1", "timestamp": "2026-01-01T00:00:00Z"}) + "\n")
        f.write("\n")
        path = f.name
    try:
        ingestor = FileIngestor()
        events = ingestor.ingest_jsonl(path)
        assert len(events) == 1
    finally:
        Path(path).unlink()


def test_ingest_proxy_log_basic():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write("# comment\n")
        f.write("GET https://api.openai.com/v1/chat/completions HTTP/1.1\n")
        f.write("\n")
        f.write("GET https://example.com/health HTTP/1.1\n")
        path = f.name
    try:
        ingestor = FileIngestor()
        events = ingestor.ingest_proxy_log(path)
        assert len(events) == 2
        assert events[0].format == "proxy_log"
        assert events[0].source == "proxy"
    finally:
        Path(path).unlink()


def test_ingest_file_dispatches_on_extension():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps({"source": "net", "raw": "line1", "timestamp": "2026-01-01T00:00:00Z"}) + "\n")
        jsonl_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write("GET https://example.com/health HTTP/1.1\n")
        log_path = f.name

    try:
        ingestor = FileIngestor()
        jsonl_events = ingestor.ingest_file(jsonl_path)
        log_events = ingestor.ingest_file(log_path)
        assert jsonl_events[0].format == "jsonl"
        assert log_events[0].format == "proxy_log"
    finally:
        Path(jsonl_path).unlink()
        Path(log_path).unlink()


# ──────────────────────────────────────────────────────────────────────────────
# HTTP ingest endpoint tests
# ──────────────────────────────────────────────────────────────────────────────


def test_http_ingest_rejects_invalid_token(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from services.ingest.http_ingest import router

    monkeypatch.setenv("THALOS_API_TOKEN", "correct-secret-token")
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/ingest/events",
        json={"events": [{"message": "test"}]},
        headers={"X-Api-Token": "wrong-token"},
    )
    assert response.status_code == 401


def test_http_ingest_rejects_unconfigured_token(monkeypatch):
    """Verify the endpoint rejects requests when THALOS_API_TOKEN is not set."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from services.ingest.http_ingest import router

    # Ensure the env var is not set (or equals default)
    monkeypatch.delenv("THALOS_API_TOKEN", raising=False)
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/ingest/events",
        json={"events": [{"message": "test"}]},
        headers={"X-Api-Token": "thalos-dev-token"},
    )
    assert response.status_code == 401


def test_http_ingest_accepts_valid_token(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from services.ingest.http_ingest import router

    monkeypatch.setenv("THALOS_API_TOKEN", "test-token-123")
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/ingest/events",
        json={"events": [{"message": "test event"}], "source": "test"},
        headers={"X-Api-Token": "test-token-123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] == 1
    assert len(data["event_ids"]) == 1
    assert len(data["input_hash"]) == 64


def test_http_ingest_batch(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from services.ingest.http_ingest import router

    monkeypatch.setenv("THALOS_API_TOKEN", "test-token")
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    events = [{"message": f"event {i}"} for i in range(5)]
    response = client.post(
        "/ingest/events",
        json={"events": events, "source": "batch-test"},
        headers={"X-Api-Token": "test-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] == 5
    assert len(data["event_ids"]) == 5
