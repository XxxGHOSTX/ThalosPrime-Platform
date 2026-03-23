"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import pytest

from thalos_core.engine.state import reset_state
from thalos_core.metrics.engine import (
    get_metrics_snapshot,
    inc_audit_writes,
    inc_ingestion_events,
    inc_ingestion_failures,
    set_sieve_score,
)
from thalos_core.metrics.schema import (
    METRIC_AUDIT_WRITES,
    METRIC_INGESTION_EVENTS,
    METRIC_INGESTION_FAILURES,
    METRIC_SIEVE_SCORE,
)


@pytest.fixture(autouse=True)
def clean_state():
    reset_state()
    yield
    reset_state()


def test_set_sieve_score():
    set_sieve_score(0.75)
    snap = get_metrics_snapshot()
    assert snap[METRIC_SIEVE_SCORE] == 0.75


def test_inc_ingestion_events():
    inc_ingestion_events()
    inc_ingestion_events()
    snap = get_metrics_snapshot()
    assert snap[METRIC_INGESTION_EVENTS] == 2


def test_inc_ingestion_failures():
    inc_ingestion_failures()
    snap = get_metrics_snapshot()
    assert snap[METRIC_INGESTION_FAILURES] == 1


def test_inc_audit_writes():
    inc_audit_writes()
    inc_audit_writes()
    inc_audit_writes()
    snap = get_metrics_snapshot()
    assert snap[METRIC_AUDIT_WRITES] == 3


def test_initial_state_zeros():
    snap = get_metrics_snapshot()
    assert snap[METRIC_SIEVE_SCORE] == 0.0
    assert snap[METRIC_INGESTION_EVENTS] == 0
    assert snap[METRIC_INGESTION_FAILURES] == 0
    assert snap[METRIC_AUDIT_WRITES] == 0


def test_snapshot_has_all_four_metrics():
    snap = get_metrics_snapshot()
    assert METRIC_SIEVE_SCORE in snap
    assert METRIC_INGESTION_EVENTS in snap
    assert METRIC_INGESTION_FAILURES in snap
    assert METRIC_AUDIT_WRITES in snap
