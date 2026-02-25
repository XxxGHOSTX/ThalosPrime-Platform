"""
PROPRIETARY AND CONFIDENTIAL
Copyright © 2026 Tony Ray Macier III. All Rights Reserved.
This code implements the Thalos Prime Sovereign Discovery Logic.
"""
import uuid
from hashlib import sha256
import json
from datetime import datetime, timezone
from .seed_manager import ThalosSeedManager
from .state_store import ThalosStateStore


class ThalosSessionManager:
    """Multi-turn context and session lifecycle manager."""

    def __init__(self):
        self.seed_manager = ThalosSeedManager()
        self.state_store = ThalosStateStore()
        self._sessions: dict[str, dict] = {}

    def create_session(self, context: dict | None = None) -> str:
        session_id = str(uuid.uuid4())
        seed = self.seed_manager.derive_execution_seed(context or {}, session_id)
        self._sessions[session_id] = {
            "id": session_id,
            "seed": seed,
            "context": context or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "turns": [],
        }
        state_hash = sha256(json.dumps(self._sessions[session_id], sort_keys=True).encode()).hexdigest()
        self.state_store.write_event(session_id, "SESSION_CREATED", self._sessions[session_id], state_hash)
        return session_id

    def add_turn(self, session_id: str, role: str, content: str) -> str:
        if session_id not in self._sessions:
            raise KeyError(f"Session {session_id} not found")
        turn = {"role": role, "content": content, "timestamp": datetime.now(timezone.utc).isoformat()}
        self._sessions[session_id]["turns"].append(turn)
        state_hash = sha256(json.dumps(turn, sort_keys=True).encode()).hexdigest()
        self.state_store.write_event(session_id, "TURN_ADDED", turn, state_hash)
        return state_hash

    def get_session(self, session_id: str) -> dict | None:
        return self._sessions.get(session_id)
