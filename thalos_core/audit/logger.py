"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

from thalos_core.audit.formatter import format_audit_entry
from thalos_core.audit.writer import append_audit_entry
from thalos_core.metrics.engine import inc_audit_writes


def log_event(seed: int, query: str, result_hash: str, state_hash: str, metrics: dict) -> None:
    entry = format_audit_entry(seed, query, result_hash, state_hash, metrics)
    append_audit_entry(entry)
    inc_audit_writes()
