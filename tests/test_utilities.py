"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utilities import compute_sha256, validate_seed, now_iso


def test_sha256_dict():
    h = compute_sha256({"key": "value"})
    assert len(h) == 64
    assert h == compute_sha256({"key": "value"})


def test_sha256_string():
    h = compute_sha256("hello")
    assert len(h) == 64


def test_validate_seed_valid():
    assert validate_seed(9876543210123456) == 9876543210123456


def test_validate_seed_zero_raises():
    with pytest.raises(ValueError):
        validate_seed(0)


def test_validate_seed_none_raises():
    with pytest.raises(ValueError):
        validate_seed(None)


def test_now_iso_format():
    ts = now_iso()
    assert "T" in ts
    assert ts.endswith("+00:00") or ts.endswith("Z") or "+" in ts
