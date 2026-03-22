#!/usr/bin/env bash
# PROPRIETARY AND CONFIDENTIAL
# Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
# This script implements the Thalos Prime Sovereign Discovery Logic.
set -euo pipefail

SEED="${SEED:-2026032100000001}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export THALOS_SEED="$SEED"

echo "[run_stack] Starting full Thalos Prime stack with seed=$SEED"
cd "$REPO_ROOT"
docker compose -f infrastructure/docker/docker-compose.yml up --build
