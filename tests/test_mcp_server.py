"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))  # noqa: E402

from services.discovery_sentinel.mcp_server import app  # noqa: E402

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "thalos-sentinel-mcp"


def test_list_tools_returns_all_tools():
    response = client.post("/tools/list", json={})
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    tool_names = [t["name"] for t in data["tools"]]
    assert "sentinel/run-scan" in tool_names
    assert "sentinel/risk-report" in tool_names
    assert "sentinel/agentic-audit" in tool_names


def test_run_scan_no_findings():
    response = client.post(
        "/tools/call",
        json={"name": "sentinel/run-scan", "arguments": {"log_entries": [], "seed": 9876543210123456}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["isError"] is False
    assert "state_hash" in data


def test_run_scan_detects_shadow_ai():
    response = client.post(
        "/tools/call",
        json={
            "name": "sentinel/run-scan",
            "arguments": {
                "log_entries": ["GET https://api.openai.com/v1/chat/completions"],
                "seed": 9876543210123456,
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["isError"] is False
    # Content should mention the finding
    assert "SHADOW_AI_DETECTED" in data["content"][0]["text"]


def test_risk_report_tool():
    findings = [{"alert": "SHADOW_AI_DETECTED", "endpoint": "api.openai.com"}]
    response = client.post(
        "/tools/call",
        json={"name": "sentinel/risk-report", "arguments": {"findings": findings, "seed": 9876543210123456}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["isError"] is False
    assert data["risk_level"] == "CRITICAL"
    assert data["risk_score"] >= 80


def test_agentic_audit_tool():
    html = '<a href="/llms.txt">LLMs</a><script type="application/ld+json">{}</script>'
    response = client.post(
        "/tools/call",
        json={
            "name": "sentinel/agentic-audit",
            "arguments": {"url": "https://example.com", "html_content": html},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["isError"] is False
    assert data["agentic_score"] >= 30


def test_unknown_tool_returns_error():
    response = client.post(
        "/tools/call",
        json={"name": "sentinel/nonexistent", "arguments": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["isError"] is True


def test_run_scan_is_deterministic():
    logs = ["GET https://api.openai.com/v1/chat/completions"]
    r1 = client.post(
        "/tools/call",
        json={"name": "sentinel/run-scan", "arguments": {"log_entries": logs, "seed": 9876543210123456}},
    )
    r2 = client.post(
        "/tools/call",
        json={"name": "sentinel/run-scan", "arguments": {"log_entries": logs, "seed": 9876543210123456}},
    )
    assert r1.json()["state_hash"] == r2.json()["state_hash"]
