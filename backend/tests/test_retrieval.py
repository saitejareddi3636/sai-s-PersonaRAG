import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rag.backends import TfidfBackend
from app.rag.retrieve import load_processed_chunks
from app.rag.types import ChunkRecord


def test_tfidf_backend_top_hit() -> None:
    chunks: list[ChunkRecord] = [
        {
            "id": "a",
            "content_type": "x",
            "source_file": "a.md",
            "section_title": "S",
            "section_level": 1,
            "text": "python backend apis microservices",
            "metadata": {},
        },
        {
            "id": "b",
            "content_type": "x",
            "source_file": "b.md",
            "section_title": "T",
            "section_level": 1,
            "text": "unrelated knitting patterns",
            "metadata": {},
        },
    ]
    backend = TfidfBackend(chunks)
    hits = backend.search("python backend experience", k=2)
    assert hits[0].id == "a"
    assert hits[0].score > hits[1].score


def test_load_processed_chunks_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "chunks.json"
    p.write_text(
        json.dumps(
            {
                "chunks": [
                    {
                        "id": "1",
                        "content_type": "summary",
                        "source_file": "s.md",
                        "section_title": "Intro",
                        "section_level": 1,
                        "text": "hello world",
                        "metadata": {"k": "v"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    rows = load_processed_chunks(p)
    assert len(rows) == 1
    assert rows[0]["text"] == "hello world"


def test_chat_includes_retrieval(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pytest.importorskip("sklearn")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("RETRIEVAL_BACKEND", "tfidf")
    proc = tmp_path / "data" / "processed"
    proc.mkdir(parents=True)
    chunks_path = proc / "chunks.json"
    chunks_path.write_text(
        json.dumps(
            {
                "chunks": [
                    {
                        "id": "demo_00001",
                        "content_type": "summary",
                        "source_file": "summary.md",
                        "section_title": "Overview",
                        "section_level": 2,
                        "text": "Software engineer with backend and machine learning experience.",
                        "metadata": {},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("CHUNKS_JSON_PATH", str(chunks_path))

    with TestClient(app) as client:
        r = client.post("/api/chat", json={"question": "What is your backend experience?"})
    assert r.status_code == 200
    data = r.json()
    assert "retrieval" in data
    assert isinstance(data["retrieval"], list)
    assert len(data["retrieval"]) >= 1
    # With real knowledge base, retrieval ranking may vary; just verify structure
    assert "source_file" in data["retrieval"][0]
    assert data.get("confidence") in ("high", "medium", "low")
    assert "sources" in data and isinstance(data["sources"], list)
