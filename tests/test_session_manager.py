"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.control_plane.session_manager import ThalosSessionManager


def _make_manager() -> ThalosSessionManager:
    """Create a ThalosSessionManager with a temporary state store DB."""
    mgr = ThalosSessionManager.__new__(ThalosSessionManager)
    from services.control_plane.seed_manager import ThalosSeedManager
    from services.control_plane.state_store import ThalosStateStore

    mgr.seed_manager = ThalosSeedManager()
    mgr.state_store = ThalosStateStore(db_path=tempfile.mktemp(suffix=".db"))
    mgr._sessions = {}
    return mgr


def test_create_session_returns_uuid():
    mgr = _make_manager()
    sid = mgr.create_session()
    assert isinstance(sid, str)
    assert len(sid) == 36  # UUID format


def test_create_session_with_context():
    mgr = _make_manager()
    sid = mgr.create_session(context={"user": "test"})
    session = mgr.get_session(sid)
    assert session is not None
    assert session["context"] == {"user": "test"}


def test_session_has_seed():
    mgr = _make_manager()
    sid = mgr.create_session()
    session = mgr.get_session(sid)
    assert "seed" in session
    assert isinstance(session["seed"], int)
    assert session["seed"] > 0


def test_add_turn_returns_hash():
    mgr = _make_manager()
    sid = mgr.create_session()
    h = mgr.add_turn(sid, "user", "Hello, Thalos.")
    assert isinstance(h, str)
    assert len(h) == 64  # SHA-256 hex digest


def test_add_turn_missing_session_raises():
    mgr = _make_manager()
    with pytest.raises(KeyError):
        mgr.add_turn("nonexistent-session", "user", "hello")


def test_turns_accumulate():
    mgr = _make_manager()
    sid = mgr.create_session()
    mgr.add_turn(sid, "user", "First message")
    mgr.add_turn(sid, "assistant", "First response")
    session = mgr.get_session(sid)
    assert len(session["turns"]) == 2
    assert session["turns"][0]["role"] == "user"
    assert session["turns"][1]["role"] == "assistant"


def test_get_nonexistent_session_returns_none():
    mgr = _make_manager()
    assert mgr.get_session("does-not-exist") is None
