"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.discovery_sentinel.scanner import SentinelScanner


def test_detects_openai():
    scanner = SentinelScanner()
    result = scanner.audit_traffic("GET https://api.openai.com/v1/chat/completions HTTP/1.1")
    assert result is not None
    assert result["alert"] == "SHADOW_AI_DETECTED"
    assert result["risk_level"] == "CRITICAL"


def test_detects_anthropic():
    scanner = SentinelScanner()
    result = scanner.audit_traffic("POST https://api.anthropic.com/v1/messages")
    assert result is not None
    assert result["alert"] == "SHADOW_AI_DETECTED"


def test_clean_traffic_returns_none():
    scanner = SentinelScanner()
    result = scanner.audit_traffic("GET https://example.com/api/data HTTP/1.1")
    assert result is None


def test_bulk_audit():
    scanner = SentinelScanner()
    logs = [
        "GET https://api.openai.com/v1/chat/completions",
        "GET https://example.com/health",
        "POST https://api.anthropic.com/v1/messages",
    ]
    findings = scanner.audit_bulk(logs)
    assert len(findings) == 2
