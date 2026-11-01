# Control-plane session API security

The session API now requires a bearer token for every `/sessions` endpoint and binds each session to the identity represented by the token. Requests from a different identity receive the same 404 response as a missing session so the API does not disclose whether another identity's session exists.

## Required configuration

Set `THALOS_CONTROL_PLANE_API_TOKENS` to a JSON object mapping a client identity to a unique random bearer token. Each token must contain at least 32 UTF-8 bytes. Do not commit the production values or place them in public issue comments.

Example shape only (not a usable secret):

```json
{"sentinel":"REPLACE_WITH_A_UNIQUE_RANDOM_TOKEN_OF_32_OR_MORE_BYTES","operator":"REPLACE_WITH_A_DIFFERENT_RANDOM_TOKEN_OF_32_OR_MORE_BYTES"}
```

Generate tokens with a cryptographically secure generator, then configure the JSON value in the deployment secret manager or a local untracked environment file. Tokens must be unique per principal; the service fails closed if configuration is missing, malformed, weak, or reuses the same token for multiple identities. Clients must send `Authorization: Bearer <token>`.

The health endpoint remains public for container liveness probes. Session creation, turn writes, and session reads require authentication. The Docker Compose port mapping is loopback-only by default; use an authenticated reverse proxy and explicit network controls if remote access is needed.

## Validation and residual risks

The regression tests cover authentication enforcement, fail-closed configuration, token identity, and cross-principal read/write isolation. These changes do not encrypt existing database files, review historical Git objects, or establish whether a prior deployment was reachable. Inspect existing state stores/backups and deployment logs separately. Never rewrite history until the historical database is safely preserved for offline examination and GitHub's sensitive-data-removal process has been reviewed.
