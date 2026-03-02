# REPRODUCIBILITY — Thalos Prime Platform

> PROPRIETARY AND CONFIDENTIAL  
> Copyright © 2026 Tony Ray Macier III. All Rights Reserved.

## Determinism Guarantee

Thalos Prime is designed for **deterministic, seed-reproducible core artifacts**: given the same seed and the same input files, every pipeline run produces identical versioned artifacts, hashes, and manifests. Operational metadata such as `generated_at`, `session_id`, and STATELOG timestamps is intentionally non-deterministic and excluded from this guarantee.

---

## How Determinism Is Achieved

### 1. Seed-driven execution

Every pipeline run requires an explicit `--seed` argument. The seed is a positive 64-bit integer that is incorporated into:

- The `input_hash` (SHA-256 of `{seed, raw_lines}`)
- Every firewall rule ID (SHA-256 of `{seed}:{endpoint}`)
- Every patch hash (SHA-256 of `{seed, vulnerability}`)
- The `pipeline_state_hash` (SHA-256 of `{seed, input_hash, findings}`)

No Python `random`, `uuid`, or time-based values are mixed into the artifact content — only SHA-256 functions seeded with deterministic inputs.

### 2. Sorted JSON serialization

All SHA-256 computations over dicts use `json.dumps(..., sort_keys=True)` to guarantee a canonical byte representation regardless of dict insertion order.

### 3. Frozen event schema

`IngestEvent` is a Pydantic v2 frozen model — events cannot be mutated after creation, preventing accidental non-determinism.

---

## Running the Determinism Check

```bash
python -m pytest tests/test_determinism.py -v
```

Key tests:

| Test | What it verifies |
|------|-----------------|
| `test_pipeline_is_deterministic` | Same seed + same input → identical state hashes, artifact hashes, rule IDs |
| `test_pipeline_different_seeds_produce_different_hashes` | Different seeds → different outputs |
| `test_pipeline_writes_statelog` | Audit log is written with correct seed and pipeline ID |

---

## Running a Reproducibility Regression

```bash
# First run
python -m automation.pipeline_cli \
  --seed 9876543210123456 \
  --input logs/network.log \
  --output output/run-001

# Second run (identical inputs)
python -m automation.pipeline_cli \
  --seed 9876543210123456 \
  --input logs/network.log \
  --output output/run-002

# Compare manifests
diff <(python3 -c "import json; d=json.load(open('output/run-001/manifest.json')); d.pop('generated_at',''); d.pop('manifest_sha256',''); print(json.dumps(d, indent=2))") \
     <(python3 -c "import json; d=json.load(open('output/run-002/manifest.json')); d.pop('generated_at',''); d.pop('manifest_sha256',''); print(json.dumps(d, indent=2))")
```

The only fields that differ across runs are `generated_at` (wall-clock timestamp) and `manifest_sha256` (which changes because `generated_at` changes). All artifact-level hashes, `pipeline_state_hash`, `input_hash`, and `session_id` are identical.

---

## Artifact Manifest

Every pipeline run produces `output/<dir>/manifest.json`:

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-01T12:00:00Z",
  "seed": 9876543210123456,
  "input_hash": "sha256-of-seed-and-raw-lines",
  "platform_version": "2.0.0",
  "session_id": "uuid",
  "risk_level": "CRITICAL",
  "risk_score": 90,
  "events_ingested": 3,
  "findings_count": 1,
  "artifacts": [
    {
      "index": 0,
      "rule_id": "abc123def456",
      "rule_file": "firewall_rule_0000_abc123def456.txt",
      "rule_sha256": "sha256-of-rule-file",
      "patch_file": "patch_0000.txt",
      "patch_sha256": "sha256-of-patch-file",
      "finding": { ... }
    }
  ],
  "pipeline_state_hash": "sha256-of-pipeline-state",
  "manifest_sha256": "sha256-of-manifest-json-itself"
}
```

---

## Non-Deterministic Fields

The following fields intentionally vary across runs and are **excluded** from regression comparisons:

| Field | Why it varies |
|-------|--------------|
| `generated_at` | Wall-clock timestamp |
| `session_id` | UUID4 derived from wall-clock in session manager |
| `manifest_sha256` | SHA-256 of manifest including `generated_at` |
| STATELOG `timestamp` | Wall-clock timestamp |
