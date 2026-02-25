"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.control_plane.seed_manager import ThalosSeedManager


def test_seed_is_deterministic():
    mgr = ThalosSeedManager()
    seed1 = mgr.derive_execution_seed({"event": "scan"}, "session-001")
    seed2 = mgr.derive_execution_seed({"event": "scan"}, "session-001")
    assert seed1 == seed2


def test_different_sessions_produce_different_seeds():
    mgr = ThalosSeedManager()
    seed1 = mgr.derive_execution_seed({"event": "scan"}, "session-001")
    seed2 = mgr.derive_execution_seed({"event": "scan"}, "session-002")
    assert seed1 != seed2


def test_seed_is_positive_integer():
    mgr = ThalosSeedManager()
    seed = mgr.derive_execution_seed({}, "test-session")
    assert isinstance(seed, int)
    assert seed > 0


def test_seed_is_64bit():
    mgr = ThalosSeedManager()
    seed = mgr.derive_execution_seed({}, "test-session")
    assert seed < 2 ** 64
