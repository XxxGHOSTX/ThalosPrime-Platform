"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import json
import os
from pathlib import Path

_REPO_ROOT = Path(os.environ.get("THALOS_ROOT", str(Path(__file__).resolve().parents[3])))
AUDIT_FILE = _REPO_ROOT / "runtime" / "statelog" / "events.jsonl"


def ensure_audit_file() -> None:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_FILE.exists():
        AUDIT_FILE.touch()


def append_audit_entry(entry: dict) -> None:
    ensure_audit_file()
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
