"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from thalos_core.utils.seed_guard import require_seed

app = FastAPI(title="Sentinel Discovery", version="1.0.0")

_SEED: int = 0


@app.get("/")
def root() -> dict:
    return {"service": "sentinel-discovery", "version": "1.0.0", "seed": _SEED}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> PlainTextResponse:
    output = (
        "# TYPE thalos_sentinel_scans_total counter\n"
        "thalos_sentinel_scans_total 0\n"
        "# TYPE thalos_sentinel_discoveries_total counter\n"
        "thalos_sentinel_discoveries_total 0\n"
    )
    return PlainTextResponse(output, media_type="text/plain; version=0.0.4")


def main() -> None:
    global _SEED
    _SEED = require_seed()
    host = "127.0.0.1"
    port = 8001
    args = sys.argv[1:]
    if "--host" in args:
        host = args[args.index("--host") + 1]
    if "--port" in args:
        port = int(args[args.index("--port") + 1])
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
