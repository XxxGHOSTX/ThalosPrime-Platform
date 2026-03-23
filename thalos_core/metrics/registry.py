"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

from thalos_core.metrics.schema import METRIC_TYPES


def validate_export_render(rendered: str) -> bool:
    for metric_name, metric_type in METRIC_TYPES.items():
        expected = f"# TYPE {metric_name} {metric_type}"
        if expected not in rendered:
            return False
    return True
