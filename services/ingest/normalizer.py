"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import hashlib

from core.utilities import now_iso
from .schema import IngestEvent, NormalizedEvent


class EventNormalizer:
    """Transforms a raw IngestEvent into a NormalizedEvent with a deterministic hash and UTC timestamp."""

    def normalize(self, event: IngestEvent) -> NormalizedEvent:
        """
        Normalize an IngestEvent.

        Computes a SHA-256 digest of the raw payload and stamps the current UTC time
        as ``normalized_at``.  All original event fields are preserved verbatim.
        """
        input_hash = hashlib.sha256(event.raw.encode()).hexdigest()
        return NormalizedEvent(
            event_id=event.event_id,
            source=event.source,
            raw=event.raw,
            timestamp=event.timestamp,
            format=event.format,
            severity=event.severity,
            metadata=event.metadata,
            normalized_at=now_iso(),
            input_hash=input_hash,
        )
