"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
import sys
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from system.orchestrator import ThalosOrchestrator


def _temp_statelog() -> str:
    tmp = tempfile.mktemp(suffix=".jsonl")
    return tmp


def test_pipeline_runs_with_valid_seed():
    orch = ThalosOrchestrator(seed=9876543210123456, statelog_path=_temp_statelog())
    result = orch.run_discovery_pipeline([])
    assert "risk_level" in result
    assert result["risk_level"] == "LOW"  # no findings → low risk


def test_pipeline_detects_shadow_ai():
    orch = ThalosOrchestrator(seed=9876543210123456, statelog_path=_temp_statelog())
    logs = ["GET https://api.openai.com/v1/chat/completions HTTP/1.1"]
    result = orch.run_discovery_pipeline(logs)
    assert result["risk_level"] == "CRITICAL"
    assert result["risk_score"] >= 80
    assert len(result["findings"]) == 1


def test_pipeline_result_has_state_hash():
    orch = ThalosOrchestrator(seed=9876543210123456, statelog_path=_temp_statelog())
    result = orch.run_discovery_pipeline([])
    assert "state_hash" in result
    assert len(result["state_hash"]) == 64


def test_pipeline_is_deterministic():
    path1 = _temp_statelog()
    path2 = _temp_statelog()
    logs = ["GET https://api.openai.com/v1/chat/completions"]
    orch1 = ThalosOrchestrator(seed=9876543210123456, statelog_path=path1)
    orch2 = ThalosOrchestrator(seed=9876543210123456, statelog_path=path2)
    r1 = orch1.run_discovery_pipeline(logs)
    r2 = orch2.run_discovery_pipeline(logs)
    assert r1["state_hash"] == r2["state_hash"]


def test_invalid_seed_raises():
    with pytest.raises(ValueError):
        ThalosOrchestrator(seed=0)


def test_statelog_written():
    path = _temp_statelog()
    orch = ThalosOrchestrator(seed=9876543210123456, statelog_path=path)
    orch.run_discovery_pipeline([])
    assert Path(path).exists()
    import json
    lines = Path(path).read_text().strip().splitlines()
    assert len(lines) >= 1
    record = json.loads(lines[0])
    assert record["pipeline"] == "discovery"
    assert record["seed"] == 9876543210123456
