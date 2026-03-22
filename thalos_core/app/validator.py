"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

from thalos_core.audit.writer import AUDIT_FILE, ensure_audit_file
from thalos_core.engine.state import get_state
from thalos_core.metrics.engine import get_metrics_snapshot


def validate_startup() -> bool:
    try:
        ensure_audit_file()
    except Exception as exc:
        raise RuntimeError(f"Audit file initialization failed: {exc}") from exc
    if not AUDIT_FILE.parent.exists():
        raise RuntimeError(f"Audit directory does not exist: {AUDIT_FILE.parent}")
    try:
        get_metrics_snapshot()
    except Exception as exc:
        raise RuntimeError(f"Metrics registry initialization failed: {exc}") from exc
    try:
        get_state()
    except Exception as exc:
        raise RuntimeError(f"State initialization failed: {exc}") from exc
    return True
