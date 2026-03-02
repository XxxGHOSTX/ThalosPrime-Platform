"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.

⚠️  EXPERIMENTAL TEST STUB — NOT STABLE
"""

import pytest
from experimental.experiment_template.experiment import ExperimentStub


def test_experiment_requires_valid_seed():
    with pytest.raises(ValueError):
        ExperimentStub(seed=0)


def test_experiment_run_returns_dict():
    exp = ExperimentStub(seed=9876543210123456)
    result = exp.run({"input": "test"})
    assert isinstance(result, dict)
    assert result["is_experimental"] is True
    assert result["seed"] == 9876543210123456
