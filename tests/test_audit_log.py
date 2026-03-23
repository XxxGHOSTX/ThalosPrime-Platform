"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import json
import tempfile
from pathlib import Path

import pytest

from thalos_core.audit.formatter import format_audit_entry
from thalos_core.engine.state import reset_state

SEED = 2026032100000001


@pytest.fixture(autouse=True)
def clean_state():
    reset_state()
    yield
    reset_state()


def test_format_audit_entry_structure():
    metrics = {
        "thalos_sieve_score": 0.5,
        "thalos_ingestion_events_total": 1,
        "thalos_ingestion_failures_total": 0,
        "thalos_audit_writes_total": 0,
    }
    entry = format_audit_entry(SEED, "test_query", "abc123", "def456", metrics)
    assert entry["seed"] == SEED
    assert entry["query"] == "test_query"
    assert entry["hash"] == "abc123"
    assert entry["state_hash"] == "def456"
    assert entry["event"] == "metrics_update"
    assert "metrics" in entry


def test_format_audit_entry_metrics_keys():
    metrics = {
        "thalos_sieve_score": 0.5,
        "thalos_ingestion_events_total": 1,
        "thalos_ingestion_failures_total": 0,
        "thalos_audit_writes_total": 0,
    }
    entry = format_audit_entry(SEED, "query", "h1", "h2", metrics)
    m = entry["metrics"]
    assert "thalos_sieve_score" in m
    assert "thalos_ingestion_events_total" in m
    assert "thalos_ingestion_failures_total" in m
    assert "thalos_audit_writes_total" in m


def test_append_audit_entry_creates_file():
    import thalos_core.audit.writer as writer_module

    with tempfile.TemporaryDirectory() as tmpdir:
        test_audit_file = Path(tmpdir) / "statelog" / "events.jsonl"
        original_audit_file = writer_module.AUDIT_FILE
        writer_module.AUDIT_FILE = test_audit_file
        try:
            from thalos_core.audit.writer import append_audit_entry

            entry = {"seed": SEED, "query": "test", "event": "test_event"}
            append_audit_entry(entry)
            assert test_audit_file.exists()
            content = test_audit_file.read_text()
            parsed = json.loads(content.strip())
            assert parsed["seed"] == SEED
        finally:
            writer_module.AUDIT_FILE = original_audit_file


def test_append_audit_entry_jsonl_format():
    import thalos_core.audit.writer as writer_module

    with tempfile.TemporaryDirectory() as tmpdir:
        test_audit_file = Path(tmpdir) / "statelog" / "events.jsonl"
        original_audit_file = writer_module.AUDIT_FILE
        writer_module.AUDIT_FILE = test_audit_file
        try:
            from thalos_core.audit.writer import append_audit_entry

            entry1 = {"id": 1, "event": "test"}
            entry2 = {"id": 2, "event": "test2"}
            append_audit_entry(entry1)
            append_audit_entry(entry2)
            lines = test_audit_file.read_text().strip().split("\n")
            assert len(lines) == 2
            assert json.loads(lines[0])["id"] == 1
            assert json.loads(lines[1])["id"] == 2
        finally:
            writer_module.AUDIT_FILE = original_audit_file
