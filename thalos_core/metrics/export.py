"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

from thalos_core.engine.state import reset_state
from thalos_core.metrics.engine import render_prometheus_metrics


def initialize_metrics() -> None:
    reset_state()


def get_prometheus_output() -> str:
    return render_prometheus_metrics()
