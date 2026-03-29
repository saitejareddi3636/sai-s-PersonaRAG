from pathlib import Path

from app.rag.ingest import ingest_documents, run_ingestion


def test_ingest_documents_minimal(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "demo.md").write_text("# Section\n\nHello world.\n", encoding="utf-8")

    payload = ingest_documents(repo_root=tmp_path, max_chars=500, overlap=50)
    assert payload["chunk_count"] == 1
    assert payload["chunks"][0]["content_type"] == "demo"
    assert payload["chunks"][0]["section_title"] == "Section"
    assert "Hello world" in payload["chunks"][0]["text"]


def test_run_ingestion_writes_file(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "x.md").write_text("# A\n\nB", encoding="utf-8")
    out = tmp_path / "out" / "chunks.json"
    path = run_ingestion(repo_root=tmp_path, output_path=out)
    assert path == out
    assert path.is_file()
    assert path.read_text(encoding="utf-8").strip().startswith("{")
