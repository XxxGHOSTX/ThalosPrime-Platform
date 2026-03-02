# CONFIGURATION — Thalos Prime Platform

> PROPRIETARY AND CONFIDENTIAL  
> Copyright © 2026 Tony Ray Macier III. All Rights Reserved.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `THALOS_SEED` | _(required)_ | 64-bit integer execution seed. All pipeline runs require this. |
| `THALOS_API_TOKEN` | `thalos-dev-token` | API token for HTTP ingest endpoint authentication. |
| `DATABASE_URL` | `sqlite:///STATELOG/state.db` | State store database URL. SQLite WAL by default. |
| `STATELOG_PATH` | `STATELOG/events.jsonl` | Path to the JSONL audit event log. |
| `OWNER` | `Tony Ray Macier III` | Platform owner identifier embedded in audit records. |
| `PLATFORM_VERSION` | `2.0.0` | Platform version injected into manifests and audit records. |
| `LOG_LEVEL` | `INFO` | Python logging level (`DEBUG`, `INFO`, `WARN`, `ERROR`). |

## Service Ports

| Service | Port | Protocol |
|---------|------|----------|
| Control Plane | 8000 | HTTP |
| Sentinel MCP | 8001 | HTTP |
| Prometheus | 9090 | HTTP |

## Seed Requirements

Every generator, scanner, and pipeline run **must** receive an explicit `--seed` argument or `THALOS_SEED` environment variable. Omitting the seed causes an immediate exit with code 1.

The seed must be a positive 64-bit integer (1 – 2^64 – 1).

## SQLite WAL State Store

State is persisted in `STATELOG/state.db` using SQLite in WAL (Write-Ahead Logging) mode for concurrent read safety.

In Kubernetes, the state file lives on a `PersistentVolumeClaim` mounted at `/app/STATELOG`.

### Backup strategy

```bash
# Backup state DB
sqlite3 STATELOG/state.db ".backup STATELOG/state-backup-$(date +%Y%m%d).db"
```

### Retention

The STATELOG JSONL file grows unbounded. Implement rotation externally (e.g., logrotate or a cron job) to keep disk usage bounded.

## API Token Security

The `THALOS_API_TOKEN` is validated with `hmac.compare_digest` (constant-time) to prevent timing oracle attacks.

**The ingest endpoint rejects all requests if `THALOS_API_TOKEN` is not set** — there is no insecure default. You must set a strong secret token before the endpoint accepts any traffic.

In production, inject the token via Kubernetes Secret (see `infrastructure/kubernetes/secrets-template.yml`).

## Prometheus Scrape Configuration

See `infrastructure/monitoring/prometheus.yml`. Both services expose a `/metrics` endpoint:
- Control Plane (`thalos-core:8000/metrics`) — session/turn counters and request latency
- Sentinel MCP (`thalos-sentinel:8001/metrics`) — scan count and findings counter
