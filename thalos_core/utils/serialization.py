"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import json


def to_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def from_json(s: str) -> dict:
    return json.loads(s)


def to_jsonl_line(obj: dict) -> str:
    return json.dumps(obj)
