"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))  # noqa: E402

from services.control_plane.main import app  # noqa: E402

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "thalos-control-plane"
    assert data["version"] == "2.0.0"
    assert data["owner"] == "Tony Ray Macier III"


def test_create_session_returns_201():
    response = client.post("/sessions", json={"context": {}})
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert "seed" in data
    assert isinstance(data["seed"], int)
    assert data["seed"] > 0


def test_create_session_with_context():
    response = client.post("/sessions", json={"context": {"user": "test-user"}})
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data


def test_add_turn_to_session():
    # Create session first
    create_resp = client.post("/sessions", json={"context": {}})
    session_id = create_resp.json()["session_id"]

    # Add a turn
    turn_resp = client.post(
        f"/sessions/{session_id}/turns",
        json={"role": "user", "content": "Hello Thalos"},
    )
    assert turn_resp.status_code == 200
    data = turn_resp.json()
    assert "state_hash" in data
    assert data["session_id"] == session_id
    assert len(data["state_hash"]) == 64


def test_add_turn_to_missing_session_returns_404():
    response = client.post(
        "/sessions/nonexistent-uuid/turns",
        json={"role": "user", "content": "Hello"},
    )
    assert response.status_code == 404


def test_get_session():
    # Create session and add a turn
    create_resp = client.post("/sessions", json={"context": {"test": True}})
    session_id = create_resp.json()["session_id"]
    client.post(f"/sessions/{session_id}/turns", json={"role": "user", "content": "Hi"})

    # Retrieve session
    get_resp = client.get(f"/sessions/{session_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == session_id
    assert len(data["turns"]) == 1
    assert data["turns"][0]["role"] == "user"


def test_get_missing_session_returns_404():
    response = client.get("/sessions/does-not-exist")
    assert response.status_code == 404


def test_multiple_turns_accumulate():
    create_resp = client.post("/sessions", json={"context": {}})
    session_id = create_resp.json()["session_id"]

    client.post(f"/sessions/{session_id}/turns", json={"role": "user", "content": "First"})
    client.post(f"/sessions/{session_id}/turns", json={"role": "assistant", "content": "Response"})

    get_resp = client.get(f"/sessions/{session_id}")
    turns = get_resp.json()["turns"]
    assert len(turns) == 2
    assert turns[0]["role"] == "user"
    assert turns[1]["role"] == "assistant"


def test_metrics_endpoint_returns_prometheus_format():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "thalos_sessions_created_total" in response.text
    assert "thalos_turns_added_total" in response.text


def test_ingest_endpoint_present(monkeypatch):
    """Verify the ingest router is mounted on the control plane."""
    monkeypatch.setenv("THALOS_API_TOKEN", "cp-test-token")
    response = client.post(
        "/ingest/events",
        json={"events": [{"msg": "test"}], "source": "test"},
        headers={"X-Api-Token": "cp-test-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] == 1
