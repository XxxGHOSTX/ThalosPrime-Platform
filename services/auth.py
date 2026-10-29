"""Shared fail-closed bearer-token authentication for Thalos Prime services."""

import hmac
import os

from fastapi import Header, HTTPException


def require_api_token(authorization: str | None = Header(default=None)) -> None:
    """Require a configured bearer token for protected HTTP operations."""
    expected = os.environ.get("THALOS_API_TOKEN", "")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Protected API is unavailable until THALOS_API_TOKEN is configured",
        )

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Bearer authentication is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, separator, supplied = authorization.partition(" ")
    if (
        not separator
        or scheme.lower() != "bearer"
        or not hmac.compare_digest(supplied, expected)
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
