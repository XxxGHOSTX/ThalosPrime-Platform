# RUNBOOK — Thalos Prime Platform

> PROPRIETARY AND CONFIDENTIAL  
> Copyright © 2026 Tony Ray Macier III. All Rights Reserved.

## Overview

This runbook covers day-to-day operations for the Thalos Prime Sovereign Discovery Platform.

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker + Docker Compose
- pip

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### Run tests

```bash
pytest tests/ -v --tb=short
```

### Run lint

```bash
ruff check . --output-format=github
ruff format --check .
```

### Run the determinism check (pipeline CLI)

```bash
python -m automation.pipeline_cli \
  --seed 9876543210123456 \
  --input logs/network.log \
  --output output/run-001
```

Output artifacts will appear in `output/run-001/`, including `manifest.json` with SHA-256 hashes.

### Run the control plane locally

```bash
python -m services.control_plane.main --seed 9876543210123456 --host 127.0.0.1 --port 8000
```

### Run the sentinel MCP server

```bash
python -m services.discovery_sentinel.mcp_server --seed 9876543210123456 --host 127.0.0.1 --port 8001
```

---

## Docker Compose (Full Stack)

```bash
# From repo root
cd infra/
THALOS_API_TOKEN=my-secret-token docker compose up --build
```

Services:
| Name | Port | Description |
|------|------|-------------|
| thalos-core | 8000 | Control Plane + Ingest HTTP API |
| thalos-sentinel | 8001 | Sentinel MCP Server |
| prometheus | 9090 | Metrics scraper |

Health checks:
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

Prometheus metrics:
```bash
curl http://localhost:8000/metrics
```

---

## Kubernetes Deployment

### Apply manifests

```bash
kubectl apply -f infrastructure/kubernetes/namespace.yml
kubectl apply -f infrastructure/kubernetes/configmap.yml
# Create the secret with real values (NOT the template):
kubectl create secret generic thalos-secrets \
  --namespace=thalos-prime \
  --from-literal=execution-seed=9876543210123456 \
  --from-literal=api-token=my-secret-token
kubectl apply -f infrastructure/kubernetes/pvc.yml
kubectl apply -f infrastructure/kubernetes/deployment.yml
kubectl apply -f infrastructure/kubernetes/service.yml
```

### Verify deployment

```bash
kubectl get pods -n thalos-prime
kubectl logs -n thalos-prime deploy/thalos-core
kubectl port-forward -n thalos-prime svc/thalos-core-svc 8000:80
curl http://localhost:8000/health
```

---

## HTTP Ingest API

Send events to the control plane:

```bash
curl -X POST http://localhost:8000/ingest/events \
  -H "Content-Type: application/json" \
  -H "X-Api-Token: ${THALOS_API_TOKEN}" \
  -d '{"events": [{"message": "suspicious egress detected"}], "source": "network-tap"}'
```

---

## VS Code Extension

Build:
```bash
cd extension/
npm install
npm run build
```

The compiled extension will be in `extension/dist/`.

---

## STATELOG

All pipeline events are written to `STATELOG/events.jsonl`. Each line is a JSON record with:
- `timestamp` — ISO 8601 UTC
- `seed` — execution seed used
- `state_hash` — SHA-256 of the event payload
- `session_id` — control-plane session

---

## Prometheus Metrics

Scraped from `/metrics` on each service. Key metrics:
- `thalos_sessions_created_total` — sessions opened
- `thalos_turns_added_total` — turns appended
- `thalos_request_duration_seconds` — per-endpoint latency histogram
