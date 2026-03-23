"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import pytest

from thalos_core.engine.mnn import run_mnn
from thalos_core.engine.state import get_state, reset_state

SEED = 2026032100000001


@pytest.fixture(autouse=True)
def clean_state():
    reset_state()
    yield
    reset_state()


def test_run_mnn_deterministic_same_inputs():
    state = get_state()
    result1 = run_mnn(SEED, "test_query", state)
    result2 = run_mnn(SEED, "test_query", state)
    assert result1["hash"] == result2["hash"]
    assert result1["sieve_score"] == result2["sieve_score"]


def test_run_mnn_different_query():
    state = get_state()
    result1 = run_mnn(SEED, "query_a", state)
    result2 = run_mnn(SEED, "query_b", state)
    assert result1["hash"] != result2["hash"]


def test_run_mnn_different_seed():
    state = get_state()
    result1 = run_mnn(SEED, "test_query", state)
    result2 = run_mnn(SEED + 1, "test_query", state)
    assert result1["hash"] != result2["hash"]


def test_run_mnn_result_structure():
    state = get_state()
    result = run_mnn(SEED, "test_query", state)
    assert "hash" in result
    assert "sieve_score" in result
    assert "seed" in result
    assert "query" in result
    assert "features" in result
    features = result["features"]
    assert "hash_prefix" in features
    assert "score_band" in features
    assert "entropy_bucket" in features


def test_run_mnn_sieve_score_range():
    state = get_state()
    result = run_mnn(SEED, "test_query", state)
    assert 0.0 <= result["sieve_score"] <= 1.0


def test_run_mnn_score_band_values():
    state = get_state()
    for q in ["a", "b", "c", "d", "e", "f", "g", "h"]:
        result = run_mnn(SEED, q, state)
        assert result["features"]["score_band"] in ("low", "mid", "high")


def test_run_mnn_entropy_bucket_range():
    state = get_state()
    for q in ["a", "b", "c", "d", "e", "f", "g", "h"]:
        result = run_mnn(SEED, q, state)
        assert 0 <= result["features"]["entropy_bucket"] <= 7


def test_run_mnn_hash_prefix_length():
    state = get_state()
    result = run_mnn(SEED, "test_query", state)
    assert len(result["features"]["hash_prefix"]) == 16


def test_run_mnn_excludes_updated_at_from_hash():
    state1 = get_state()
    state2 = dict(state1)
    state2["updated_at"] = "2099-01-01T00:00:00Z"
    result1 = run_mnn(SEED, "test_query", state1)
    result2 = run_mnn(SEED, "test_query", state2)
    assert result1["hash"] == result2["hash"]
