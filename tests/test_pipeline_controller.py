"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from system.pipeline_controller import PipelineController, PipelineRun, PipelineStatus


def test_create_run():
    ctrl = PipelineController()
    run = ctrl.create_run("pipeline-001", seed=9876543210123456)
    assert run.pipeline_id == "pipeline-001"
    assert run.seed == 9876543210123456
    assert run.status == PipelineStatus.PENDING


def test_get_run():
    ctrl = PipelineController()
    ctrl.create_run("pipeline-002", seed=9876543210123456)
    run = ctrl.get_run("pipeline-002")
    assert run is not None
    assert run.pipeline_id == "pipeline-002"


def test_get_missing_run_returns_none():
    ctrl = PipelineController()
    assert ctrl.get_run("nonexistent") is None


def test_run_lifecycle():
    ctrl = PipelineController()
    run = ctrl.create_run("pipeline-003", seed=9876543210123456)

    run.start()
    assert run.status == PipelineStatus.RUNNING
    assert run.started_at is not None

    run.complete({"findings": 0})
    assert run.status == PipelineStatus.COMPLETED
    assert run.completed_at is not None
    assert len(run.steps) == 1


def test_run_fail():
    ctrl = PipelineController()
    run = ctrl.create_run("pipeline-004", seed=9876543210123456)
    run.start()
    run.fail("Connection timeout")
    assert run.status == PipelineStatus.FAILED
    assert run.error == "Connection timeout"
    assert run.completed_at is not None


def test_list_runs():
    ctrl = PipelineController()
    ctrl.create_run("p1", seed=9876543210123456)
    ctrl.create_run("p2", seed=9876543210123456)
    runs = ctrl.list_runs()
    assert len(runs) == 2


def test_state_hash_is_sha256():
    ctrl = PipelineController()
    run = ctrl.create_run("pipeline-hash", seed=9876543210123456)
    h = run.state_hash()
    assert isinstance(h, str)
    assert len(h) == 64
