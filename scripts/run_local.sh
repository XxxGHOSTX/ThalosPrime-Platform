#!/usr/bin/env bash
# PROPRIETARY AND CONFIDENTIAL
# Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
# This script implements the Thalos Prime Sovereign Discovery Logic.
set -euo pipefail

SEED="${SEED:-2026032100000001}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export THALOS_ROOT="$REPO_ROOT"

echo "[run_local] Starting thalos-core with seed=$SEED"
exec python -m thalos_core.app.main --seed "$SEED" --host 0.0.0.0 --port 8000
