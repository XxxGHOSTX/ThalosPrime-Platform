"""Authentication regression tests for the Thalos control plane."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.control_plane.main import app

TOKEN = "test-token-for-thalos-prime-platform-tests-000000"


@pytest.fixture(autouse=True)
def configure_test_token(monkeypatch):
    monkeypatch.setenv("THALOS_API_TOKEN", TOKEN)


client = TestClient(app, headers={"Authorization": f"Bearer {TOKEN}"})


def test_health_is_public():
    response = TestClient(app).get("/health")
    assert response.status_code == 200


def test_session_creation_requires_authentication():
    response = TestClient(app).post("/sessions", json={"context": {}})
    assert response.status_code == 401


def test_session_creation_accepts_valid_token():
    response = client.post("/sessions", json={"context": {"purpose": "test"}})
    assert response.status_code == 201
    assert "session_id" in response.json()


def test_session_read_rejects_invalid_token():
    response = TestClient(app, headers={"Authorization": "Bearer wrong"}).get("/sessions/not-a-session")
    assert response.status_code == 401


def test_missing_server_token_fails_closed(monkeypatch):
    monkeypatch.delenv("THALOS_API_TOKEN")
    response = TestClient(app).post("/sessions", json={"context": {}})
    assert response.status_code == 503


def test_short_server_token_fails_closed(monkeypatch):
    monkeypatch.setenv("THALOS_API_TOKEN", "too-short")
    response = TestClient(app).post("/sessions", json={"context": {}})
    assert response.status_code == 503


def test_valid_length_token_rejects_wrong_value(monkeypatch):
    monkeypatch.setenv("THALOS_API_TOKEN", TOKEN)
    response = TestClient(
        app,
        headers={"Authorization": "Bearer " + ("x" * len(TOKEN))},
    ).post("/sessions", json={"context": {}})
    assert response.status_code == 401
