"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys

import uvicorn
from fastapi import FastAPI

from thalos_core.app.lifecycle import lifespan
from thalos_core.app.routes import router, set_app_seed
from thalos_core.utils.seed_guard import require_seed


def create_app(seed: int) -> FastAPI:
    app = FastAPI(title="Thalos Core", version="1.0.0", lifespan=lifespan)
    set_app_seed(seed)
    app.include_router(router)
    return app


def main() -> None:
    seed = require_seed()
    host = "127.0.0.1"
    port = 8000
    args = sys.argv[1:]
    if "--host" in args:
        host = args[args.index("--host") + 1]
    if "--port" in args:
        port = int(args[args.index("--port") + 1])
    app = create_app(seed)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
