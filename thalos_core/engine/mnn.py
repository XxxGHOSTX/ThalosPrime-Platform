"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

from thalos_core.engine.deterministic_hash import sha256_state


def run_mnn(seed: int, query: str, state: dict) -> dict:
    hash_hex = sha256_state(seed, query, state)
    sieve_score = int(hash_hex[:8], 16) / 0xFFFFFFFF
    if sieve_score < 0.33:
        score_band = "low"
    elif sieve_score < 0.66:
        score_band = "mid"
    else:
        score_band = "high"
    entropy_bucket = int(hash_hex[8:10], 16) % 8
    hash_prefix = hash_hex[:16]
    return {
        "hash": hash_hex,
        "sieve_score": sieve_score,
        "seed": seed,
        "query": query,
        "features": {
            "hash_prefix": hash_prefix,
            "score_band": score_band,
            "entropy_bucket": entropy_bucket,
        },
    }
