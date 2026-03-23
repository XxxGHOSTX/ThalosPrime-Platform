"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""


class ThalosError(Exception):
    pass


class SeedError(ThalosError):
    pass


class StateError(ThalosError):
    pass


class AuditError(ThalosError):
    pass


class MetricsError(ThalosError):
    pass
