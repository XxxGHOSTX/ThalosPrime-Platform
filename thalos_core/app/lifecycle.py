"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from thalos_core.app.validator import validate_startup
from thalos_core.engine.state import reset_state
from thalos_core.metrics.export import initialize_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_startup()
    initialize_metrics()
    reset_state()
    yield
