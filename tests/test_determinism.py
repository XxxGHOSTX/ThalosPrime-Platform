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

from automation.pipeline_cli import run_pipeline  # noqa: E402


def _write_log_file(lines: list[str], suffix: str = ".log") -> str:
    """Write lines to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
    for line in lines:
        f.write(line + "\n")
    f.flush()
    f.close()
    return f.name


def _temp_statelog() -> str:
    """Create a secure temporary JSONL file path for STATELOG output."""
    f = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
    f.close()
    return f.name


def test_pipeline_runs_empty_input():
    with tempfile.TemporaryDirectory() as out_dir:
        log_file = _write_log_file([])
        statelog = _temp_statelog()
        try:
            manifest = run_pipeline(
                seed=9876543210123456,
                input_paths=[log_file],
                output_dir=out_dir,
                statelog_path=statelog,
            )
            assert manifest["risk_level"] == "LOW"
            assert manifest["findings_count"] == 0
            assert manifest["seed"] == 9876543210123456
        finally:
            Path(log_file).unlink(missing_ok=True)
            Path(statelog).unlink(missing_ok=True)


def test_pipeline_detects_shadow_ai():
    with tempfile.TemporaryDirectory() as out_dir:
        log_file = _write_log_file(["GET https://api.openai.com/v1/chat/completions HTTP/1.1"])
        statelog = _temp_statelog()
        try:
            manifest = run_pipeline(
                seed=9876543210123456,
                input_paths=[log_file],
                output_dir=out_dir,
                statelog_path=statelog,
            )
            assert manifest["risk_level"] == "CRITICAL"
            assert manifest["findings_count"] >= 1
            assert len(manifest["artifacts"]) >= 1
        finally:
            Path(log_file).unlink(missing_ok=True)
            Path(statelog).unlink(missing_ok=True)


def test_pipeline_produces_manifest_file():
    with tempfile.TemporaryDirectory() as out_dir:
        log_file = _write_log_file(["GET https://example.com/health HTTP/1.1"])
        statelog = _temp_statelog()
        try:
            run_pipeline(
                seed=9876543210123456,
                input_paths=[log_file],
                output_dir=out_dir,
                statelog_path=statelog,
            )
            manifest_path = Path(out_dir) / "manifest.json"
            assert manifest_path.exists()
            saved = json.loads(manifest_path.read_text())
            assert saved["seed"] == 9876543210123456
            assert "manifest_sha256" in saved
        finally:
            Path(log_file).unlink(missing_ok=True)
            Path(statelog).unlink(missing_ok=True)


def test_pipeline_manifest_has_required_fields():
    with tempfile.TemporaryDirectory() as out_dir:
        log_file = _write_log_file([])
        statelog = _temp_statelog()
        try:
            manifest = run_pipeline(
                seed=9876543210123456,
                input_paths=[log_file],
                output_dir=out_dir,
                statelog_path=statelog,
            )
            required = [
                "schema_version",
                "generated_at",
                "seed",
                "input_hash",
                "platform_version",
                "session_id",
                "risk_level",
                "risk_score",
                "events_ingested",
                "findings_count",
                "artifacts",
                "pipeline_state_hash",
            ]
            for field in required:
                assert field in manifest, f"Missing field: {field}"
        finally:
            Path(log_file).unlink(missing_ok=True)
            Path(statelog).unlink(missing_ok=True)


def test_pipeline_is_deterministic():
    """Bit-for-bit identical output for same seed + same input."""
    lines = ["GET https://api.openai.com/v1/chat/completions HTTP/1.1"]
    log_file = _write_log_file(lines)
    sl1, sl2 = _temp_statelog(), _temp_statelog()

    try:
        with tempfile.TemporaryDirectory() as out1, tempfile.TemporaryDirectory() as out2:
            m1 = run_pipeline(
                seed=9876543210123456,
                input_paths=[log_file],
                output_dir=out1,
                statelog_path=sl1,
            )
            m2 = run_pipeline(
                seed=9876543210123456,
                input_paths=[log_file],
                output_dir=out2,
                statelog_path=sl2,
            )
            # Core deterministic fields must be identical
            assert m1["pipeline_state_hash"] == m2["pipeline_state_hash"]
            assert m1["input_hash"] == m2["input_hash"]
            assert m1["risk_level"] == m2["risk_level"]
            assert m1["risk_score"] == m2["risk_score"]
            assert m1["findings_count"] == m2["findings_count"]
            # Artifact-level hashes must be identical
            for a1, a2 in zip(m1["artifacts"], m2["artifacts"]):
                assert a1["rule_sha256"] == a2["rule_sha256"]
                assert a1["patch_sha256"] == a2["patch_sha256"]
                assert a1["rule_id"] == a2["rule_id"]
    finally:
        Path(log_file).unlink(missing_ok=True)
        Path(sl1).unlink(missing_ok=True)
        Path(sl2).unlink(missing_ok=True)


def test_pipeline_different_seeds_produce_different_hashes():
    lines = ["GET https://api.openai.com/v1/chat/completions HTTP/1.1"]
    log_file = _write_log_file(lines)
    sl1, sl2 = _temp_statelog(), _temp_statelog()

    try:
        with tempfile.TemporaryDirectory() as out1, tempfile.TemporaryDirectory() as out2:
            m1 = run_pipeline(
                seed=9876543210123456,
                input_paths=[log_file],
                output_dir=out1,
                statelog_path=sl1,
            )
            m2 = run_pipeline(
                seed=1111111111111111,
                input_paths=[log_file],
                output_dir=out2,
                statelog_path=sl2,
            )
            # Different seeds → different state hashes
            assert m1["pipeline_state_hash"] != m2["pipeline_state_hash"]
            # Different seeds → different artifact rule IDs
            assert m1["artifacts"][0]["rule_id"] != m2["artifacts"][0]["rule_id"]
    finally:
        Path(log_file).unlink(missing_ok=True)
        Path(sl1).unlink(missing_ok=True)
        Path(sl2).unlink(missing_ok=True)


def test_pipeline_invalid_seed_raises():
    with tempfile.TemporaryDirectory() as out_dir:
        with pytest.raises(ValueError):
            run_pipeline(
                seed=0,
                input_paths=[],
                output_dir=out_dir,
                statelog_path=_temp_statelog(),
            )


def test_pipeline_writes_statelog():
    with tempfile.TemporaryDirectory() as out_dir:
        log_file = _write_log_file([])
        statelog = _temp_statelog()
        try:
            run_pipeline(
                seed=9876543210123456,
                input_paths=[log_file],
                output_dir=out_dir,
                statelog_path=statelog,
            )
            assert Path(statelog).exists()
            lines = Path(statelog).read_text().strip().splitlines()
            assert len(lines) >= 1
            record = json.loads(lines[0])
            assert record["pipeline"] == "cli"
            assert record["seed"] == 9876543210123456
        finally:
            Path(log_file).unlink(missing_ok=True)
            Path(statelog).unlink(missing_ok=True)
