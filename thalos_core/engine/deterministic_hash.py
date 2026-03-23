"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import hashlib
import json


def canonical_payload(seed: int, query: str, state: dict) -> bytes:
    filtered_state = {k: v for k, v in state.items() if k != "updated_at"}
    payload = json.dumps(
        {"seed": seed, "query": query, "state": filtered_state},
        sort_keys=True,
        separators=(",", ":"),
    )
    return payload.encode("utf-8")


def sha256_state(seed: int, query: str, state: dict) -> str:
    return hashlib.sha256(canonical_payload(seed, query, state)).hexdigest()
