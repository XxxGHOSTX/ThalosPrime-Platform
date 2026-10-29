"""Authentication and per-principal isolation tests for the control-plane session API."""
import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))  # noqa: E402

from services.control_plane.main import app  # noqa: E402

client = TestClient(app)
TOKENS = {
    "alice": "test-token-for-alice-0123456789-ABCDEF",
    "bob": "test-token-for-bob-0123456789-ABCDEF",
}


@pytest.fixture(autouse=True)
def _configured_tokens(monkeypatch):
    monkeypatch.setenv("THALOS_CONTROL_PLANE_API_TOKENS", json.dumps(TOKENS))


def _auth_headers(identity="alice"):
    return {"Authorization": f"Bearer {TOKENS[identity]}"}


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "thalos-control-plane"
    assert data["version"] == "2.0.0"
    assert data["owner"] == "Tony Ray Macier III"


def test_session_endpoints_require_authentication():
    response = client.post("/sessions", json={"context": {}})
    assert response.status_code == 401


def test_missing_auth_configuration_fails_closed(monkeypatch):
    monkeypatch.delenv("THALOS_CONTROL_PLANE_API_TOKENS", raising=False)
    response = client.post("/sessions", json={"context": {}}, headers=_auth_headers())
    assert response.status_code == 503


def test_create_session_returns_201():
    response = client.post("/sessions", json={"context": {}}, headers=_auth_headers())
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert "seed" in data
    assert isinstance(data["seed"], int)
    assert data["seed"] > 0


def test_create_session_with_context():
    response = client.post(
        "/sessions",
        json={"context": {"user": "test-user"}},
        headers=_auth_headers(),
    )
    assert response.status_code == 201
    assert "session_id" in response.json()


def test_add_turn_to_session():
    create_resp = client.post("/sessions", json={"context": {}}, headers=_auth_headers())
    session_id = create_resp.json()["session_id"]
    turn_resp = client.post(
        f"/sessions/{session_id}/turns",
        json={"role": "user", "content": "Hello Thalos"},
        headers=_auth_headers(),
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
        headers=_auth_headers(),
    )
    assert response.status_code == 404


def test_get_session():
    create_resp = client.post(
        "/sessions",
        json={"context": {"test": True}},
        headers=_auth_headers(),
    )
    session_id = create_resp.json()["session_id"]
    client.post(
        f"/sessions/{session_id}/turns",
        json={"role": "user", "content": "Hi"},
        headers=_auth_headers(),
    )
    get_resp = client.get(f"/sessions/{session_id}", headers=_auth_headers())
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == session_id
    assert len(data["turns"]) == 1
    assert data["turns"][0]["role"] == "user"
    assert "_owner_id" not in data


def test_get_missing_session_returns_404():
    response = client.get("/sessions/does-not-exist", headers=_auth_headers())
    assert response.status_code == 404


def test_other_principal_cannot_read_or_mutate_a_session():
    create_resp = client.post("/sessions", json={"context": {}}, headers=_auth_headers("alice"))
    session_id = create_resp.json()["session_id"]

    read_resp = client.get(f"/sessions/{session_id}", headers=_auth_headers("bob"))
    assert read_resp.status_code == 404

    write_resp = client.post(
        f"/sessions/{session_id}/turns",
        json={"role": "user", "content": "unauthorized write"},
        headers=_auth_headers("bob"),
    )
    assert write_resp.status_code == 404

    own_resp = client.get(f"/sessions/{session_id}", headers=_auth_headers("alice"))
    assert own_resp.status_code == 200
    assert own_resp.json()["turns"] == []


def test_multiple_turns_accumulate():
    create_resp = client.post("/sessions", json={"context": {}}, headers=_auth_headers())
    session_id = create_resp.json()["session_id"]
    client.post(
        f"/sessions/{session_id}/turns",
        json={"role": "user", "content": "First"},
        headers=_auth_headers(),
    )
    client.post(
        f"/sessions/{session_id}/turns",
        json={"role": "assistant", "content": "Response"},
        headers=_auth_headers(),
    )
    get_resp = client.get(f"/sessions/{session_id}", headers=_auth_headers())
    turns = get_resp.json()["turns"]
    assert len(turns) == 2
    assert turns[0]["role"] == "user"
    assert turns[1]["role"] == "assistant"
