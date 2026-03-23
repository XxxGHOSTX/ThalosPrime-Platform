"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import pytest

from thalos_core.engine.state import reset_state
from thalos_core.metrics.engine import inc_ingestion_events, render_prometheus_metrics, set_sieve_score
from thalos_core.metrics.registry import validate_export_render


@pytest.fixture(autouse=True)
def clean_state():
    reset_state()
    yield
    reset_state()


def test_render_prometheus_metrics_contains_type_lines():
    output = render_prometheus_metrics()
    assert "# TYPE thalos_sieve_score gauge" in output
    assert "# TYPE thalos_ingestion_events_total counter" in output
    assert "# TYPE thalos_ingestion_failures_total counter" in output
    assert "# TYPE thalos_audit_writes_total counter" in output


def test_render_prometheus_metrics_contains_values():
    set_sieve_score(0.42)
    inc_ingestion_events()
    output = render_prometheus_metrics()
    assert "thalos_sieve_score 0.42" in output
    assert "thalos_ingestion_events_total 1" in output


def test_render_prometheus_metrics_trailing_newline():
    output = render_prometheus_metrics()
    assert output.endswith("\n")


def test_validate_export_render_valid():
    output = render_prometheus_metrics()
    assert validate_export_render(output) is True


def test_validate_export_render_missing_type():
    bad_output = "thalos_sieve_score 0.0\n"
    assert validate_export_render(bad_output) is False


def test_render_prometheus_metrics_format():
    output = render_prometheus_metrics()
    lines = output.strip().split("\n")
    assert len(lines) == 8
    assert lines[0].startswith("# TYPE")
    assert lines[2].startswith("# TYPE")
    assert lines[4].startswith("# TYPE")
    assert lines[6].startswith("# TYPE")
