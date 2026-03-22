"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import copy
import threading

_DEFAULT_STATE = {
    "thalos_sieve_score": 0.0,
    "thalos_ingestion_events_total": 0,
    "thalos_ingestion_failures_total": 0,
    "thalos_audit_writes_total": 0,
    "last_query": "",
    "last_seed": 0,
    "last_hash": "",
    "updated_at": "",
}

_state: dict = copy.deepcopy(_DEFAULT_STATE)
_lock: threading.Lock = threading.Lock()


def get_state() -> dict:
    with _lock:
        return copy.deepcopy(_state)


def set_state(key: str, value) -> None:
    with _lock:
        _state[key] = value


def update_state(mapping: dict) -> None:
    with _lock:
        _state.update(mapping)


def snapshot_state() -> dict:
    with _lock:
        return copy.deepcopy(_state)


def reset_state() -> None:
    with _lock:
        _state.clear()
        _state.update(copy.deepcopy(_DEFAULT_STATE))
