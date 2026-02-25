"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.base_engine import ExecutionContext, BaseEngine, MODULE_VERSION, MODULE_OWNER


# ── ExecutionContext tests ─────────────────────────────────────────────────────

def test_execution_context_state_hash_is_sha256():
    ctx = ExecutionContext(seed=9876543210123456, session_id="test-session")
    h = ctx.state_hash()
    assert isinstance(h, str)
    assert len(h) == 64


def test_execution_context_state_hash_is_deterministic():
    ctx1 = ExecutionContext(seed=9876543210123456, session_id="s1")
    ctx2 = ExecutionContext(seed=9876543210123456, session_id="s1")
    assert ctx1.state_hash() == ctx2.state_hash()


def test_different_seeds_produce_different_hashes():
    ctx1 = ExecutionContext(seed=1111111111111111, session_id="s1")
    ctx2 = ExecutionContext(seed=2222222222222222, session_id="s1")
    assert ctx1.state_hash() != ctx2.state_hash()


def test_execution_context_defaults():
    ctx = ExecutionContext(seed=9876543210123456, session_id="s1")
    assert ctx.owner == MODULE_OWNER
    assert ctx.version == MODULE_VERSION
    assert "T" in ctx.created_at


# ── BaseEngine tests ───────────────────────────────────────────────────────────

class ConcreteEngine(BaseEngine):
    """Minimal concrete subclass for testing BaseEngine."""

    def execute(self, context: ExecutionContext, payload: dict) -> dict:
        return self._build_response(context, {"processed": True, "input": payload})


def test_base_engine_build_response():
    engine = ConcreteEngine()
    ctx = ExecutionContext(seed=9876543210123456, session_id="s-test")
    result = engine.execute(ctx, {"data": "scan"})
    assert "state_hash" in result
    assert result["version"] == MODULE_VERSION
    assert result["session_id"] == "s-test"
    assert result["seed"] == 9876543210123456
    assert result["result"]["processed"] is True


def test_base_engine_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        BaseEngine()  # type: ignore
