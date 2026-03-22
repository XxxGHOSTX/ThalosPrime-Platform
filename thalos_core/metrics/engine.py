"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

from thalos_core.engine import state as _state_module
from thalos_core.metrics.schema import (
    METRIC_AUDIT_WRITES,
    METRIC_INGESTION_EVENTS,
    METRIC_INGESTION_FAILURES,
    METRIC_SIEVE_SCORE,
)


def set_sieve_score(value: float) -> None:
    _state_module.set_state(METRIC_SIEVE_SCORE, value)


def inc_ingestion_events() -> None:
    s = _state_module.get_state()
    _state_module.set_state(METRIC_INGESTION_EVENTS, s[METRIC_INGESTION_EVENTS] + 1)


def inc_ingestion_failures() -> None:
    s = _state_module.get_state()
    _state_module.set_state(METRIC_INGESTION_FAILURES, s[METRIC_INGESTION_FAILURES] + 1)


def inc_audit_writes() -> None:
    s = _state_module.get_state()
    _state_module.set_state(METRIC_AUDIT_WRITES, s[METRIC_AUDIT_WRITES] + 1)


def get_metrics_snapshot() -> dict:
    s = _state_module.get_state()
    return {
        METRIC_SIEVE_SCORE: s[METRIC_SIEVE_SCORE],
        METRIC_INGESTION_EVENTS: s[METRIC_INGESTION_EVENTS],
        METRIC_INGESTION_FAILURES: s[METRIC_INGESTION_FAILURES],
        METRIC_AUDIT_WRITES: s[METRIC_AUDIT_WRITES],
    }


def render_prometheus_metrics() -> str:
    snap = get_metrics_snapshot()
    lines = [
        f"# TYPE {METRIC_SIEVE_SCORE} gauge",
        f"{METRIC_SIEVE_SCORE} {snap[METRIC_SIEVE_SCORE]}",
        f"# TYPE {METRIC_INGESTION_EVENTS} counter",
        f"{METRIC_INGESTION_EVENTS} {snap[METRIC_INGESTION_EVENTS]}",
        f"# TYPE {METRIC_INGESTION_FAILURES} counter",
        f"{METRIC_INGESTION_FAILURES} {snap[METRIC_INGESTION_FAILURES]}",
        f"# TYPE {METRIC_AUDIT_WRITES} counter",
        f"{METRIC_AUDIT_WRITES} {snap[METRIC_AUDIT_WRITES]}",
    ]
    return "\n".join(lines) + "\n"
