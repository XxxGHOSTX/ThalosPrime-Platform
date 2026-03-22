"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import pytest

from thalos_core.utils.seed_guard import require_seed

SEED = 2026032100000001


def test_require_seed_valid():
    result = require_seed(["prog", "--seed", str(SEED)])
    assert result == SEED


def test_require_seed_missing_raises(capsys):
    with pytest.raises(SystemExit) as exc:
        require_seed(["prog"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "ERROR: --seed required" in captured.out


def test_require_seed_no_value_raises(capsys):
    with pytest.raises(SystemExit) as exc:
        require_seed(["prog", "--seed"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "ERROR: --seed required" in captured.out


def test_require_seed_non_integer_raises(capsys):
    with pytest.raises(SystemExit) as exc:
        require_seed(["prog", "--seed", "notanint"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "ERROR: --seed required" in captured.out


def test_require_seed_float_raises(capsys):
    with pytest.raises(SystemExit) as exc:
        require_seed(["prog", "--seed", "1.5"])
    assert exc.value.code == 1


def test_require_seed_zero():
    result = require_seed(["prog", "--seed", "0"])
    assert result == 0


def test_require_seed_returns_int():
    result = require_seed(["prog", "--seed", "42"])
    assert isinstance(result, int)
    assert result == 42
