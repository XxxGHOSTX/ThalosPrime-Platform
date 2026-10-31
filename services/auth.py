"""Shared fail-closed bearer-token authentication for Thalos Prime services."""

import hmac
import os

from fastapi import Header, HTTPException


_MIN_TOKEN_BYTES = 32


def require_api_token(authorization: str | None = Header(default=None)) -> None:
    """Require a high-entropy configured bearer token for protected operations.

    A missing or weak server-side token disables the protected API rather than
    silently accepting a development credential. The supplied token is compared
    only after checking its byte length to avoid unnecessary comparison work.
    """
    expected = os.environ.get("THALOS_API_TOKEN", "").encode("utf-8")
    if len(expected) < _MIN_TOKEN_BYTES:
        raise HTTPException(
            status_code=503,
            detail=(
                "Protected API is unavailable until THALOS_API_TOKEN is configured "
                "with at least 32 UTF-8 bytes"
            ),
        )

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Bearer authentication is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, separator, supplied_value = authorization.partition(" ")
    supplied = supplied_value.encode("utf-8")
    if (
        not separator
        or scheme.lower() != "bearer"
        or len(supplied) != len(expected)
        or not hmac.compare_digest(supplied, expected)
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
