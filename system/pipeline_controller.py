"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

from dataclasses import dataclass, field
from enum import Enum
from core.utilities import now_iso, compute_sha256


class PipelineStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class PipelineRun:
    pipeline_id: str
    seed: int
    status: PipelineStatus = PipelineStatus.PENDING
    steps: list[dict] = field(default_factory=list)
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None

    def start(self):
        self.status = PipelineStatus.RUNNING
        self.started_at = now_iso()

    def complete(self, result: dict):
        self.status = PipelineStatus.COMPLETED
        self.completed_at = now_iso()
        self.steps.append({"step": "final", "result": result, "timestamp": now_iso()})

    def fail(self, error: str):
        self.status = PipelineStatus.FAILED
        self.completed_at = now_iso()
        self.error = error

    def state_hash(self) -> str:
        return compute_sha256({"id": self.pipeline_id, "seed": self.seed, "steps": self.steps})


class PipelineController:
    """Manages pipeline lifecycle and step execution tracking."""

    def __init__(self):
        self._runs: dict[str, PipelineRun] = {}

    def create_run(self, pipeline_id: str, seed: int) -> PipelineRun:
        run = PipelineRun(pipeline_id=pipeline_id, seed=seed)
        self._runs[pipeline_id] = run
        return run

    def get_run(self, pipeline_id: str) -> PipelineRun | None:
        return self._runs.get(pipeline_id)

    def list_runs(self) -> list[PipelineRun]:
        return list(self._runs.values())
