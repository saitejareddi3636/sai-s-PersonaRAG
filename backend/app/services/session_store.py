"""
Bounded chat history per session. Replace `InMemorySessionStore` with a Redis-backed
implementation later by implementing the same `SessionStore` protocol.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable


@dataclass(frozen=True)
class ChatTurn:
    role: Literal["user", "assistant"]
    content: str


@runtime_checkable
class SessionStore(Protocol):
    def ensure_session(self, session_id: str | None) -> str: ...

    def get_history_text(self, session_id: str) -> str:
        """Formatted prior turns (excludes any message not yet appended)."""
        ...

    def append_turn(self, session_id: str, role: Literal["user", "assistant"], content: str) -> None: ...


class InMemorySessionStore:
    """Thread-safe FIFO history with count and total character bounds."""

    def __init__(self, max_messages: int, max_total_chars: int) -> None:
        self._max_messages = max(2, max_messages)
        self._max_total_chars = max(500, max_total_chars)
        self._sessions: dict[str, list[ChatTurn]] = {}
        self._lock = threading.Lock()

    def ensure_session(self, session_id: str | None) -> str:
        with self._lock:
            sid = (session_id or "").strip()
            if not sid:
                sid = str(uuid.uuid4())
            self._sessions.setdefault(sid, [])
            return sid

    def get_history_text(self, session_id: str) -> str:
        with self._lock:
            turns = list(self._sessions.get(session_id, []))
        if not turns:
            return ""
        lines: list[str] = []
        for t in turns:
            label = "User" if t.role == "user" else "Assistant"
            lines.append(f"{label}: {t.content}")
        return "\n".join(lines)

    def append_turn(self, session_id: str, role: Literal["user", "assistant"], content: str) -> None:
        text = content.strip()
        if not text:
            return
        if len(text) > 100_000:
            text = text[:100_000] + "…"
        with self._lock:
            turns = self._sessions.setdefault(session_id, [])
            turns.append(ChatTurn(role=role, content=text))
            self._trim(turns)

    def _trim(self, turns: list[ChatTurn]) -> None:
        while len(turns) > self._max_messages:
            turns.pop(0)
        total = sum(len(t.content) for t in turns)
        while total > self._max_total_chars and turns:
            removed = turns.pop(0)
            total -= len(removed.content)

    def clear_for_tests(self) -> None:
        with self._lock:
            self._sessions.clear()


_store: InMemorySessionStore | None = None
_store_lock = threading.Lock()


def get_session_store(max_messages: int, max_total_chars: int) -> InMemorySessionStore:
    global _store
    with _store_lock:
        if _store is None:
            _store = InMemorySessionStore(max_messages, max_total_chars)
        return _store


def reset_session_store_for_tests() -> None:
    global _store
    with _store_lock:
        if _store is not None:
            _store.clear_for_tests()
        _store = None
