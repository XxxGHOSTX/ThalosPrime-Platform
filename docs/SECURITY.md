<!-- PROPRIETARY AND CONFIDENTIAL -->
<!-- Copyright © 2026 Tony Ray Macier III. All Rights Reserved. -->

# Security Policy

## Secret Handling
- **No secrets committed to the repository.**
- All sensitive values must be stored in GitHub Secrets or environment variables.
- Reference secrets via `${{ secrets.SECRET_NAME }}` in workflows.

## Threat Model
| Threat | Mitigation |
|---|---|
| Shadow AI API calls | SentinelScanner passive detection |
| Unauthorized egress | Firewall rules via ArtifactEngine |
| Supply chain attacks | pip-audit + npm audit in CI |
| Secret leakage | gitleaks scan on every push |
| Replay attacks | Deterministic seeds prevent replay ambiguity |

## Dependency Scanning
- Python: `pip-audit` runs daily
- Node: `npm audit` runs on package changes

## Vulnerability Reporting
Report vulnerabilities privately to the owner (Tony Ray Macier III) before public disclosure.

## Static Analysis
- `bandit` scans all Python code on push to `main`
- `ruff` enforces code quality on every PR
