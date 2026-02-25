<!-- PROPRIETARY AND CONFIDENTIAL -->
<!-- Copyright © 2026 Tony Ray Macier III. All Rights Reserved. -->

# Thalos Prime — GitHub Copilot Governance Instructions

## Exclusive Owner
**Tony Ray Macier III** is the sole author and owner of all code in this repository.

## Deterministic Invariant
Every script, service, or tool generating output **MUST** accept a `--seed` argument.
If the seed is missing, the service **MUST** fail with exit code 1.

## IP Header Rule
Every file created **MUST** begin with:
```python
"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
```

## No Hallucinations
Use only the pinned dependencies in `requirements.txt`. Do not invent APIs or library methods.

## Auditability
Every agent turn **MUST** be logged to `STATELOG/events.jsonl` with:
- ISO 8601 timestamp
- SHA-256 state hash
- Session ID

## Module Boundaries
- `core/` → stable primitives; no experimental dependencies
- `system/` → orchestration only; depends on `core/`
- `experimental/` → isolated; never imported by `core/` or `system/`
- `services/` → production services; depend on `core/`

## Branching
- `main` → protected, production-ready only
- `feature/*` → new features
- `fix/*` → bug fixes
- `experiment/*` → experimental work, never merged directly to main
