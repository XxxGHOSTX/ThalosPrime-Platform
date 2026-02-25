"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
import sys
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.control_plane.state_store import ThalosStateStore


def _make_store() -> ThalosStateStore:
    """Create a ThalosStateStore backed by a temporary in-memory-equivalent DB."""
    tmp = tempfile.mktemp(suffix=".db")
    return ThalosStateStore(db_path=tmp)


def test_write_and_retrieve_event():
    store = _make_store()
    store.write_event("sess-1", "TEST_EVENT", {"key": "value"}, "abc123hash")
    events = store.get_events("sess-1")
    assert len(events) == 1
    assert events[0]["event_type"] == "TEST_EVENT"
    assert events[0]["payload"] == {"key": "value"}
    assert events[0]["sha256_hash"] == "abc123hash"


def test_get_events_empty_session():
    store = _make_store()
    events = store.get_events("nonexistent-session")
    assert events == []


def test_multiple_events_ordered():
    store = _make_store()
    for i in range(3):
        store.write_event("sess-order", f"EVENT_{i}", {"i": i}, f"hash_{i}")
    events = store.get_events("sess-order")
    assert len(events) == 3
    assert events[0]["event_type"] == "EVENT_0"
    assert events[2]["event_type"] == "EVENT_2"


def test_session_isolation():
    store = _make_store()
    store.write_event("sess-A", "EV", {}, "h1")
    store.write_event("sess-B", "EV", {}, "h2")
    assert len(store.get_events("sess-A")) == 1
    assert len(store.get_events("sess-B")) == 1


def test_created_at_is_iso8601():
    store = _make_store()
    store.write_event("sess-ts", "EV", {}, "h")
    events = store.get_events("sess-ts")
    ts = events[0]["created_at"]
    assert "T" in ts
