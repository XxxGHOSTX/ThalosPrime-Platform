"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

from thalos_core.metrics.schema import (
    METRIC_AUDIT_WRITES,
    METRIC_INGESTION_EVENTS,
    METRIC_INGESTION_FAILURES,
    METRIC_SIEVE_SCORE,
)


def format_audit_entry(seed: int, query: str, hash_val: str, state_hash: str, metrics: dict) -> dict:
    return {
        "seed": seed,
        "query": query,
        "hash": hash_val,
        "state_hash": state_hash,
        "event": "metrics_update",
        "metrics": {
            METRIC_SIEVE_SCORE: metrics.get(METRIC_SIEVE_SCORE, 0.0),
            METRIC_INGESTION_EVENTS: metrics.get(METRIC_INGESTION_EVENTS, 0),
            METRIC_INGESTION_FAILURES: metrics.get(METRIC_INGESTION_FAILURES, 0),
            METRIC_AUDIT_WRITES: metrics.get(METRIC_AUDIT_WRITES, 0),
        },
    }
