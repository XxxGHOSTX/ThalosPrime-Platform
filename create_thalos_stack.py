#!/usr/bin/env python3
"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
# create_thalos_stack.py — idempotent writer for the complete Thalos Prime stack.
# Run once:  python create_thalos_stack.py
# Creates all required directories and source files under the repo root.

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

_HEADER = '''\
"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
'''

# ---------------------------------------------------------------------------
# File manifest: path → content
# ---------------------------------------------------------------------------
FILES: dict[str, str] = {}

# ── thalos_core/__init__.py ─────────────────────────────────────────────────
FILES["thalos_core/__init__.py"] = _HEADER

# ── thalos_core/utils/__init__.py ──────────────────────────────────────────
FILES["thalos_core/utils/__init__.py"] = _HEADER

# ── thalos_core/utils/errors.py ────────────────────────────────────────────
FILES["thalos_core/utils/errors.py"] = _HEADER + '''

class ThalosError(Exception):
    pass


class SeedError(ThalosError):
    pass


class StateError(ThalosError):
    pass


class AuditError(ThalosError):
    pass


class MetricsError(ThalosError):
    pass
'''

# ── thalos_core/utils/seed_guard.py ────────────────────────────────────────
FILES["thalos_core/utils/seed_guard.py"] = _HEADER + '''
import sys


def require_seed(argv=None) -> int:
    args = argv if argv is not None else sys.argv
    if "--seed" not in args:
        print("ERROR: --seed required")
        raise SystemExit(1)
    idx = args.index("--seed")
    if idx + 1 >= len(args):
        print("ERROR: --seed required")
        raise SystemExit(1)
    try:
        return int(args[idx + 1])
    except (ValueError, TypeError):
        print("ERROR: --seed required")
        raise SystemExit(1)
'''

# ── thalos_core/utils/serialization.py ─────────────────────────────────────
FILES["thalos_core/utils/serialization.py"] = _HEADER + '''
import json


def to_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def from_json(s: str) -> dict:
    return json.loads(s)


def to_jsonl_line(obj: dict) -> str:
    return json.dumps(obj)
'''

# ── thalos_core/engine/__init__.py ─────────────────────────────────────────
FILES["thalos_core/engine/__init__.py"] = _HEADER

# ── thalos_core/engine/deterministic_hash.py ───────────────────────────────
FILES["thalos_core/engine/deterministic_hash.py"] = _HEADER + '''
import hashlib
import json


def canonical_payload(seed: int, query: str, state: dict) -> bytes:
    filtered_state = {k: v for k, v in state.items() if k != "updated_at"}
    payload = json.dumps(
        {"seed": seed, "query": query, "state": filtered_state},
        sort_keys=True,
        separators=(",", ":"),
    )
    return payload.encode("utf-8")


def sha256_state(seed: int, query: str, state: dict) -> str:
    return hashlib.sha256(canonical_payload(seed, query, state)).hexdigest()
'''

# ── thalos_core/engine/state.py ────────────────────────────────────────────
FILES["thalos_core/engine/state.py"] = _HEADER + '''
import copy
import threading

_DEFAULT_STATE = {
    "thalos_sieve_score": 0.0,
    "thalos_ingestion_events_total": 0,
    "thalos_ingestion_failures_total": 0,
    "thalos_audit_writes_total": 0,
    "last_query": "",
    "last_seed": 0,
    "last_hash": "",
    "updated_at": "",
}

_state: dict = copy.deepcopy(_DEFAULT_STATE)
_lock: threading.Lock = threading.Lock()


def get_state() -> dict:
    with _lock:
        return copy.deepcopy(_state)


def set_state(key: str, value) -> None:
    with _lock:
        _state[key] = value


def update_state(mapping: dict) -> None:
    with _lock:
        _state.update(mapping)


def snapshot_state() -> dict:
    with _lock:
        return copy.deepcopy(_state)


def reset_state() -> None:
    with _lock:
        _state.clear()
        _state.update(copy.deepcopy(_DEFAULT_STATE))
'''

# ── thalos_core/engine/mnn.py ──────────────────────────────────────────────
FILES["thalos_core/engine/mnn.py"] = _HEADER + '''
from thalos_core.engine.deterministic_hash import sha256_state


def run_mnn(seed: int, query: str, state: dict) -> dict:
    hash_hex = sha256_state(seed, query, state)
    sieve_score = int(hash_hex[:8], 16) / 0xFFFFFFFF
    if sieve_score < 0.33:
        score_band = "low"
    elif sieve_score < 0.66:
        score_band = "mid"
    else:
        score_band = "high"
    entropy_bucket = int(hash_hex[8:10], 16) % 8
    hash_prefix = hash_hex[:16]
    return {
        "hash": hash_hex,
        "sieve_score": sieve_score,
        "seed": seed,
        "query": query,
        "features": {
            "hash_prefix": hash_prefix,
            "score_band": score_band,
            "entropy_bucket": entropy_bucket,
        },
    }
'''

# ── thalos_core/metrics/__init__.py ────────────────────────────────────────
FILES["thalos_core/metrics/__init__.py"] = _HEADER

# ── thalos_core/metrics/schema.py ──────────────────────────────────────────
FILES["thalos_core/metrics/schema.py"] = _HEADER + '''
METRIC_SIEVE_SCORE = "thalos_sieve_score"
METRIC_INGESTION_EVENTS = "thalos_ingestion_events_total"
METRIC_INGESTION_FAILURES = "thalos_ingestion_failures_total"
METRIC_AUDIT_WRITES = "thalos_audit_writes_total"

METRIC_TYPES = {
    METRIC_SIEVE_SCORE: "gauge",
    METRIC_INGESTION_EVENTS: "counter",
    METRIC_INGESTION_FAILURES: "counter",
    METRIC_AUDIT_WRITES: "counter",
}
'''

# ── thalos_core/metrics/registry.py ────────────────────────────────────────
FILES["thalos_core/metrics/registry.py"] = _HEADER + '''
from thalos_core.metrics.schema import METRIC_TYPES


def validate_export_render(rendered: str) -> bool:
    for metric_name, metric_type in METRIC_TYPES.items():
        expected = f"# TYPE {metric_name} {metric_type}"
        if expected not in rendered:
            return False
    return True
'''

# ── thalos_core/metrics/engine.py ──────────────────────────────────────────
FILES["thalos_core/metrics/engine.py"] = _HEADER + '''
from thalos_core.engine import state as _state_module
from thalos_core.metrics.schema import (
    METRIC_AUDIT_WRITES,
    METRIC_INGESTION_EVENTS,
    METRIC_INGESTION_FAILURES,
    METRIC_SIEVE_SCORE,
)


def set_sieve_score(value: float) -> None:
    _state_module.set_state(METRIC_SIEVE_SCORE, value)


def inc_ingestion_events() -> None:
    s = _state_module.get_state()
    _state_module.set_state(METRIC_INGESTION_EVENTS, s[METRIC_INGESTION_EVENTS] + 1)


def inc_ingestion_failures() -> None:
    s = _state_module.get_state()
    _state_module.set_state(METRIC_INGESTION_FAILURES, s[METRIC_INGESTION_FAILURES] + 1)


def inc_audit_writes() -> None:
    s = _state_module.get_state()
    _state_module.set_state(METRIC_AUDIT_WRITES, s[METRIC_AUDIT_WRITES] + 1)


def get_metrics_snapshot() -> dict:
    s = _state_module.get_state()
    return {
        METRIC_SIEVE_SCORE: s[METRIC_SIEVE_SCORE],
        METRIC_INGESTION_EVENTS: s[METRIC_INGESTION_EVENTS],
        METRIC_INGESTION_FAILURES: s[METRIC_INGESTION_FAILURES],
        METRIC_AUDIT_WRITES: s[METRIC_AUDIT_WRITES],
    }


def render_prometheus_metrics() -> str:
    snap = get_metrics_snapshot()
    lines = [
        f"# TYPE {METRIC_SIEVE_SCORE} gauge",
        f"{METRIC_SIEVE_SCORE} {snap[METRIC_SIEVE_SCORE]}",
        f"# TYPE {METRIC_INGESTION_EVENTS} counter",
        f"{METRIC_INGESTION_EVENTS} {snap[METRIC_INGESTION_EVENTS]}",
        f"# TYPE {METRIC_INGESTION_FAILURES} counter",
        f"{METRIC_INGESTION_FAILURES} {snap[METRIC_INGESTION_FAILURES]}",
        f"# TYPE {METRIC_AUDIT_WRITES} counter",
        f"{METRIC_AUDIT_WRITES} {snap[METRIC_AUDIT_WRITES]}",
    ]
    return "\\n".join(lines) + "\\n"
'''

# ── thalos_core/metrics/export.py ──────────────────────────────────────────
FILES["thalos_core/metrics/export.py"] = _HEADER + '''
from thalos_core.engine.state import reset_state
from thalos_core.metrics.engine import render_prometheus_metrics


def initialize_metrics() -> None:
    reset_state()


def get_prometheus_output() -> str:
    return render_prometheus_metrics()
'''

# ── thalos_core/audit/__init__.py ──────────────────────────────────────────
FILES["thalos_core/audit/__init__.py"] = _HEADER

# ── thalos_core/audit/formatter.py ─────────────────────────────────────────
FILES["thalos_core/audit/formatter.py"] = _HEADER + '''
from thalos_core.metrics.schema import (
    METRIC_AUDIT_WRITES,
    METRIC_INGESTION_EVENTS,
    METRIC_INGESTION_FAILURES,
    METRIC_SIEVE_SCORE,
)


def format_audit_entry(seed: int, query: str, hash_val: str, state_hash: str, metrics: dict) -> dict:
    return {
        "seed": seed,
        "query": query,
        "hash": hash_val,
        "state_hash": state_hash,
        "event": "metrics_update",
        "metrics": {
            METRIC_SIEVE_SCORE: metrics.get(METRIC_SIEVE_SCORE, 0.0),
            METRIC_INGESTION_EVENTS: metrics.get(METRIC_INGESTION_EVENTS, 0),
            METRIC_INGESTION_FAILURES: metrics.get(METRIC_INGESTION_FAILURES, 0),
            METRIC_AUDIT_WRITES: metrics.get(METRIC_AUDIT_WRITES, 0),
        },
    }
'''

# ── thalos_core/audit/writer.py ────────────────────────────────────────────
FILES["thalos_core/audit/writer.py"] = _HEADER + '''
import json
import os
from pathlib import Path

_REPO_ROOT = Path(os.environ.get("THALOS_ROOT", str(Path(__file__).resolve().parents[3])))
AUDIT_FILE = _REPO_ROOT / "runtime" / "statelog" / "events.jsonl"


def ensure_audit_file() -> None:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_FILE.exists():
        AUDIT_FILE.touch()


def append_audit_entry(entry: dict) -> None:
    ensure_audit_file()
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\\n")
'''

# ── thalos_core/audit/logger.py ────────────────────────────────────────────
FILES["thalos_core/audit/logger.py"] = _HEADER + '''
from thalos_core.audit.formatter import format_audit_entry
from thalos_core.audit.writer import append_audit_entry
from thalos_core.metrics.engine import inc_audit_writes


def log_event(seed: int, query: str, result_hash: str, state_hash: str, metrics: dict) -> None:
    entry = format_audit_entry(seed, query, result_hash, state_hash, metrics)
    append_audit_entry(entry)
    inc_audit_writes()
'''

# ── thalos_core/app/__init__.py ────────────────────────────────────────────
FILES["thalos_core/app/__init__.py"] = _HEADER

# ── thalos_core/app/validator.py ───────────────────────────────────────────
FILES["thalos_core/app/validator.py"] = _HEADER + '''
from thalos_core.audit.writer import AUDIT_FILE, ensure_audit_file
from thalos_core.engine.state import get_state
from thalos_core.metrics.engine import get_metrics_snapshot


def validate_startup() -> bool:
    try:
        ensure_audit_file()
    except Exception as exc:
        raise RuntimeError(f"Audit file initialization failed: {exc}") from exc
    if not AUDIT_FILE.parent.exists():
        raise RuntimeError(f"Audit directory does not exist: {AUDIT_FILE.parent}")
    try:
        get_metrics_snapshot()
    except Exception as exc:
        raise RuntimeError(f"Metrics registry initialization failed: {exc}") from exc
    try:
        get_state()
    except Exception as exc:
        raise RuntimeError(f"State initialization failed: {exc}") from exc
    return True
'''

# ── thalos_core/app/lifecycle.py ───────────────────────────────────────────
FILES["thalos_core/app/lifecycle.py"] = _HEADER + '''
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
'''

# ── thalos_core/app/routes.py ──────────────────────────────────────────────
FILES["thalos_core/app/routes.py"] = _HEADER + '''
import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from thalos_core.audit.logger import log_event
from thalos_core.app.validator import validate_startup
from thalos_core.engine.mnn import run_mnn
from thalos_core.engine.state import get_state, update_state
from thalos_core.metrics.engine import (
    get_metrics_snapshot,
    inc_ingestion_events,
    inc_ingestion_failures,
    render_prometheus_metrics,
    set_sieve_score,
)

router = APIRouter()

_APP_SEED: int = 0


def set_app_seed(seed: int) -> None:
    global _APP_SEED
    _APP_SEED = seed


def get_app_seed() -> int:
    return _APP_SEED


class QueryRequest(BaseModel):
    query: str


@router.get("/")
def root() -> dict:
    return {"service": "thalos-core", "version": "1.0.0", "seed_mode": "enforced"}


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict:
    try:
        validate_startup()
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/query")
def handle_query(request: QueryRequest) -> dict:
    seed = get_app_seed()
    try:
        state = get_state()
        result = run_mnn(seed, request.query, state)
        inc_ingestion_events()
        set_sieve_score(result["sieve_score"])
        update_state(
            {
                "last_query": request.query,
                "last_seed": seed,
                "last_hash": result["hash"],
                "thalos_sieve_score": result["sieve_score"],
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        )
        metrics = get_metrics_snapshot()
        log_event(seed, request.query, result["hash"], result["hash"], metrics)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        inc_ingestion_failures()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    return PlainTextResponse(render_prometheus_metrics(), media_type="text/plain; version=0.0.4")
'''

# ── thalos_core/app/main.py ────────────────────────────────────────────────
FILES["thalos_core/app/main.py"] = _HEADER + '''
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
'''

# ── services/discovery_sentinel/main.py ────────────────────────────────────
FILES["services/discovery_sentinel/main.py"] = _HEADER + '''
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
        "# TYPE thalos_sentinel_scans_total counter\\n"
        "thalos_sentinel_scans_total 0\\n"
        "# TYPE thalos_sentinel_discoveries_total counter\\n"
        "thalos_sentinel_discoveries_total 0\\n"
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
'''

# ── infrastructure/docker/Dockerfile.thalos-core ───────────────────────────
FILES["infrastructure/docker/Dockerfile.thalos-core"] = """\
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY thalos_core/ thalos_core/
COPY services/ services/

RUN mkdir -p runtime/statelog

EXPOSE 8000

ENTRYPOINT ["python", "-m", "thalos_core.app.main", "--seed"]
CMD ["2026032100000001"]
"""

# ── infrastructure/docker/docker-compose.yml ───────────────────────────────
FILES["infrastructure/docker/docker-compose.yml"] = """\
version: "3.9"

services:
  thalos-core:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.thalos-core
    ports:
      - "8000:8000"
    command: ["--seed", "2026032100000001"]
    volumes:
      - statelog:/app/runtime/statelog
    environment:
      - THALOS_ROOT=/app
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:v2.52.0
    ports:
      - "9090:9090"
    volumes:
      - ../prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    restart: unless-stopped

  grafana:
    image: grafana/grafana:10.4.3
    ports:
      - "3000:3000"
    volumes:
      - ../grafana/provisioning:/etc/grafana/provisioning:ro
      - ../grafana/dashboards:/var/lib/grafana/dashboards:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=thalos2026
    restart: unless-stopped

volumes:
  statelog:
"""

# ── infrastructure/prometheus/prometheus.yml ───────────────────────────────
FILES["infrastructure/prometheus/prometheus.yml"] = """\
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "thalos-core"
    static_configs:
      - targets: ["thalos-core:8000"]
    metrics_path: /metrics
"""

# ── infrastructure/grafana/provisioning/datasources.yml ────────────────────
FILES["infrastructure/grafana/provisioning/datasources.yml"] = """\
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
"""

# ── infrastructure/grafana/dashboards/thalos-prime.json ────────────────────
FILES["infrastructure/grafana/dashboards/thalos-prime.json"] = """\
{
  "uid": "thalos-prime-v2",
  "title": "Thalos Prime Monitor",
  "tags": ["thalos", "observability"],
  "schemaVersion": 39,
  "version": 1,
  "refresh": "10s",
  "time": {"from": "now-1h", "to": "now"},
  "panels": [
    {
      "id": 1,
      "type": "stat",
      "title": "Latest Sieve Score",
      "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
      "targets": [
        {
          "expr": "thalos_sieve_score",
          "legendFormat": "sieve_score",
          "refId": "A"
        }
      ],
      "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "orientation": "auto", "colorMode": "value"}
    },
    {
      "id": 2,
      "type": "timeseries",
      "title": "Ingestion Events Rate",
      "gridPos": {"x": 6, "y": 0, "w": 9, "h": 4},
      "targets": [
        {
          "expr": "rate(thalos_ingestion_events_total[1m])",
          "legendFormat": "events/s",
          "refId": "A"
        }
      ]
    },
    {
      "id": 3,
      "type": "timeseries",
      "title": "Ingestion Failures Rate",
      "gridPos": {"x": 15, "y": 0, "w": 9, "h": 4},
      "targets": [
        {
          "expr": "rate(thalos_ingestion_failures_total[1m])",
          "legendFormat": "failures/s",
          "refId": "A"
        }
      ]
    },
    {
      "id": 4,
      "type": "stat",
      "title": "Total Audit Writes",
      "gridPos": {"x": 0, "y": 4, "w": 6, "h": 4},
      "targets": [
        {
          "expr": "thalos_audit_writes_total",
          "legendFormat": "audit_writes",
          "refId": "A"
        }
      ],
      "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "orientation": "auto", "colorMode": "value"}
    }
  ]
}
"""

# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------

def write_files() -> None:
    created = 0
    skipped = 0
    for rel_path, content in FILES.items():
        dest = ROOT / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            skipped += 1
            print(f"  skip (exists): {rel_path}")
        else:
            dest.write_text(content, encoding="utf-8")
            created += 1
            print(f"  created: {rel_path}")
    print(f"\nDone — {created} created, {skipped} skipped.")


if __name__ == "__main__":
    print("Thalos Prime Stack Writer")
    print(f"Root: {ROOT}\n")
    write_files()
    sys.exit(0)
