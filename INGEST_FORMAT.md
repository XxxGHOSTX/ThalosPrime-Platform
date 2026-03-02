# INGEST FORMAT — Thalos Prime Platform

> PROPRIETARY AND CONFIDENTIAL  
> Copyright © 2026 Tony Ray Macier III. All Rights Reserved.

## Supported Ingest Formats

Thalos Prime accepts events in two file formats and one HTTP push format.

---

## 1. JSONL (Newline-Delimited JSON)

Files with `.jsonl` or `.ndjson` extension are parsed as JSONL.

Each line must be a valid JSON object. Blank lines are skipped.

### Field Mapping

| JSON Key | IngestEvent Field | Default |
|----------|-------------------|---------|
| `source` | `source` | `"file"` |
| `timestamp` | `timestamp` | current UTC ISO 8601 |
| `severity` | `severity` | `"INFO"` |
| (all others) | `metadata` | `{}` |
| _(full line)_ | `raw` | _(full line text)_ |

### Example

```jsonl
{"source": "network-tap", "timestamp": "2026-01-15T10:23:45Z", "severity": "WARN", "message": "GET https://api.openai.com/v1/chat/completions"}
{"source": "proxy", "timestamp": "2026-01-15T10:23:50Z", "message": "GET https://example.com/health"}
```

---

## 2. Proxy Log (Plain Text)

Files without `.jsonl` / `.ndjson` extension are treated as proxy logs (Apache combined log, Squid, etc.).

- Each non-blank, non-comment line becomes one event.
- Lines starting with `#` are skipped.
- The entire raw line is stored in `raw`.

### Example

```
# Squid access log
1642243425.123    123 192.168.1.5 TCP_MISS/200 1234 GET https://api.anthropic.com/v1/messages - DIRECT/1.2.3.4 application/json
1642243430.456     45 192.168.1.6 TCP_HIT/200   512 GET https://example.com/health - DIRECT/5.6.7.8 text/html
```

---

## 3. HTTP Push (API)

Events can be pushed via the REST API.

**Endpoint:** `POST /ingest/events`

**Authentication:** `X-Api-Token` header (HMAC constant-time comparison)

**Request body:**

```json
{
  "events": [
    {"message": "GET https://api.openai.com/v1/chat/completions"},
    {"message": "GET https://example.com/health", "severity": "INFO"}
  ],
  "source": "network-tap"
}
```

**Response:**

```json
{
  "accepted": 2,
  "event_ids": ["uuid-1", "uuid-2"],
  "input_hash": "sha256-of-combined-raw-payload"
}
```

---

## Normalized Event Schema

After ingestion, all events are normalized to a `NormalizedEvent`:

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | UUID4 string | Auto-generated unique identifier |
| `source` | string | Origin of the event |
| `raw` | string | Original raw text |
| `timestamp` | ISO 8601 string | Event time |
| `format` | `jsonl` \| `proxy_log` \| `http_push` | Ingest format |
| `severity` | `INFO` \| `WARN` \| `ERROR` \| `CRITICAL` | Event severity |
| `metadata` | dict | Additional key-value pairs |
| `normalized_at` | ISO 8601 string | Normalization timestamp |
| `input_hash` | 64-char hex string | SHA-256 of `raw` field |

---

## Scanner Input

The scanner (`SentinelScanner`) receives the `raw` text of each normalized event and scans it for patterns matching known AI API egress endpoints (OpenAI, Anthropic, Bedrock, Vertex AI, Cohere, Gemini).
