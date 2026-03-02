<!-- PROPRIETARY AND CONFIDENTIAL -->
<!-- Copyright © 2026 Tony Ray Macier III. All Rights Reserved. -->

# Contributing to Thalos Prime

## Workflow
1. Fork or branch from `main`
2. Follow the branching convention (`feature/`, `fix/`, `experiment/`)
3. Include the IP header in every new file
4. Run `ruff check .` and `pytest tests/` before opening a PR
5. Open a PR using the provided template
6. Reference the STATELOG event ID if applicable

## Issue Creation
Use the provided issue templates:
- Bug reports: `.github/ISSUE_TEMPLATE/bug_report.md`
- Feature requests: `.github/ISSUE_TEMPLATE/feature_request.md`
- Experiments: `.github/ISSUE_TEMPLATE/experiment_request.md`

## Pull Request Standards
- PRs must pass all CI checks
- At least one review required
- STATELOG hash must be included for service changes
