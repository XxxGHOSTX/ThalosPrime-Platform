#!/usr/bin/env python3
"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
# Bootstrap script — run once to create required directory scaffolding.
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

dirs = [
    "thalos_core/utils",
    "thalos_core/engine",
    "thalos_core/metrics",
    "thalos_core/audit",
    "thalos_core/app",
    "infrastructure/docker",
    "infrastructure/prometheus",
    "infrastructure/grafana/provisioning",
    "infrastructure/grafana/dashboards",
    "runtime/statelog",
    "services/discovery_sentinel",
]

for d in dirs:
    path = ROOT / d
    path.mkdir(parents=True, exist_ok=True)
    print(f"  created: {path}")

print("Bootstrap complete.")
