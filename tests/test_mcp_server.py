"""
Authentication regression tests for the Thalos Sentinel MCP HTTP API.
"""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.discovery_sentinel.mcp_server import app

TOKEN = "test-only-token"


@pytest.fixture(autouse=True)
def configure_test_token(monkeypatch):
    monkeypatch.setenv("THALOS_API_TOKEN", TOKEN)


client = TestClient(app, headers={"Authorization": f"Bearer {TOKEN}"})


def test_health_is_public():
    response = TestClient(app).get("/health")
    assert response.status_code == 200


def test_tools_list_requires_authentication():
    response = TestClient(app).post("/tools/list", json={})
    assert response.status_code == 401


def test_tools_list_accepts_valid_token():
    response = client.post("/tools/list", json={})
    assert response.status_code == 200
    assert len(response.json()["tools"]) == 3


def test_tools_call_rejects_invalid_token():
    response = TestClient(app, headers={"Authorization": "Bearer wrong"}).post(
        "/tools/call",
        json={"name": "sentinel/risk-report", "arguments": {"findings": [], "seed": 1}},
    )
    assert response.status_code == 401


def test_tools_call_requires_configured_token(monkeypatch):
    monkeypatch.delenv("THALOS_API_TOKEN")
    response = TestClient(app).post("/tools/list", json={})
    assert response.status_code == 503
