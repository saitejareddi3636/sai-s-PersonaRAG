from fastapi.testclient import TestClient


def test_chat_returns_session_id(client: TestClient) -> None:
    r = client.post("/api/chat", json={"question": "What is your background?"})
    assert r.status_code == 200
    sid = r.json().get("session_id")
    assert sid and isinstance(sid, str)


def test_chat_continues_session(client: TestClient) -> None:
    r1 = client.post("/api/chat", json={"question": "Hello"})
    assert r1.status_code == 200
    sid = r1.json()["session_id"]
    r2 = client.post("/api/chat", json={"question": "Can you elaborate?", "session_id": sid})
    assert r2.status_code == 200
    assert r2.json()["session_id"] == sid


def test_session_store_bounded() -> None:
    from app.services.session_store import InMemorySessionStore

    store = InMemorySessionStore(max_messages=4, max_total_chars=100_000)
    sid = store.ensure_session(None)
    for i in range(10):
        store.append_turn(sid, "user", f"u{i}")
        store.append_turn(sid, "assistant", f"a{i}")
    h = store.get_history_text(sid)
    assert "u0" not in h
    assert "u9" in h
