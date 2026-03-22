"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

METRIC_SIEVE_SCORE = "thalos_sieve_score"
METRIC_INGESTION_EVENTS = "thalos_ingestion_events_total"
METRIC_INGESTION_FAILURES = "thalos_ingestion_failures_total"
METRIC_AUDIT_WRITES = "thalos_audit_writes_total"

METRIC_TYPES = {
    METRIC_SIEVE_SCORE: "gauge",
    METRIC_INGESTION_EVENTS: "counter",
    METRIC_INGESTION_FAILURES: "counter",
    METRIC_AUDIT_WRITES: "counter",
}
