from fastapi.testclient import TestClient


def test_chat_returns_answer_and_retrieval(client: TestClient) -> None:
    response = client.post(
        "/api/chat",
        json={"question": "What is your background?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "confidence" in data
    assert data["confidence"] in ("high", "medium", "low")
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert "retrieval" in data
    assert isinstance(data["retrieval"], list)


def test_chat_benchmark_headers(client: TestClient) -> None:
    response = client.post(
        "/api/chat",
        json={"question": "Say hi in one sentence."},
        headers={"X-Benchmark": "1"},
    )
    assert response.status_code == 200
    assert "x-benchmark-llm-s" in {k.lower() for k in response.headers.keys()}
    assert response.headers.get("x-benchmark-retrieval-s") is not None
    assert response.headers.get("x-benchmark-chat-total-s") is not None


def test_chat_with_session_id(client: TestClient) -> None:
    response = client.post(
        "/api/chat",
        json={"question": "Hello", "session_id": "sess-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "sess-1"
    assert "confidence" in body
    assert "sources" in body
    assert "retrieval" in body
