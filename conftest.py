"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
# Root conftest.py — bootstraps the thalos_core package before test collection.
# This module-level block runs immediately when pytest imports this file,
# which happens before any test module is imported or collected.

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_SENTINEL = _ROOT / "thalos_core" / "__init__.py"

if not _SENTINEL.exists():
    result = subprocess.run(
        [sys.executable, str(_ROOT / "create_thalos_stack.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Thalos Core bootstrap failed:\n{result.stdout}\n{result.stderr}"
        )
