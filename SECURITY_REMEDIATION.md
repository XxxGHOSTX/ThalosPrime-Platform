# Thalos Prime Platform security remediation

**Status date:** 2026-10-29

The current control-plane and Sentinel MCP source exposes session and tool operations without authentication. Session IDs are not an authorization boundary. The Sentinel tool endpoints can also be invoked without an authenticated caller.

The remediation branch introduces a shared bearer-token dependency:
- Protected session and Sentinel tool routes require `Authorization: Bearer <token>`.
- The token is read from `THALOS_API_TOKEN`; no default token is embedded.
- If the token is not configured, protected operations fail closed with HTTP 503.
- Missing or invalid credentials return HTTP 401.
- Health checks remain public and return only service liveness metadata.
- Manual server defaults bind to loopback.

Set `THALOS_API_TOKEN` through a secret manager or secure runtime environment. Do not commit the token to Git, `.env.example`, logs, or issue comments.

Docker deployments that intentionally publish these APIs must provide the secret securely to each service. Port publishing alone does not create authorization. Network exposure and reverse-proxy controls still require review.

This is a remediation proposal, not a production security certification. The branch must pass tests and be reviewed before merge. Existing data and Git history are not modified.
