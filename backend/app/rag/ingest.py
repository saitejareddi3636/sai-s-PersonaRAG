from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.rag.chunking import chunk_text_by_paragraphs, split_markdown_sections
from app.rag.paths import repo_root as _repo_root


def _list_source_files(raw: Path) -> list[Path]:
    if not raw.is_dir():
        return []
    md = sorted(raw.glob("*.md"))
    js = sorted(raw.glob("*.json"))
    return md + js


def _ingest_markdown(
    path: Path,
    content_type: str,
    *,
    max_chars: int,
    overlap: int,
) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    source_file = path.name
    rows: list[dict[str, Any]] = []
    for level, title, body in split_markdown_sections(text):
        if not body.strip():
            continue
        parts = chunk_text_by_paragraphs(body, max_chars=max_chars, overlap=overlap)
        total = len(parts)
        for idx, part in enumerate(parts):
            rows.append(
                {
                    "content_type": content_type,
                    "source_file": source_file,
                    "section_title": title,
                    "section_level": level,
                    "text": part,
                    "metadata": {
                        "source_format": "markdown",
                        "chunk_index": idx,
                        "chunk_count_in_section": total,
                        "char_count": len(part),
                    },
                }
            )
    return rows


def _ingest_json(
    path: Path,
    content_type: str,
    *,
    max_chars: int,
    overlap: int,
) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    source_file = path.name
    rows: list[dict[str, Any]] = []

    def add_section(title: str, level: int, body: str) -> None:
        if not body.strip():
            return
        parts = chunk_text_by_paragraphs(body, max_chars=max_chars, overlap=overlap)
        total = len(parts)
        for idx, part in enumerate(parts):
            rows.append(
                {
                    "content_type": content_type,
                    "source_file": source_file,
                    "section_title": title,
                    "section_level": level,
                    "text": part,
                    "metadata": {
                        "source_format": "json",
                        "chunk_index": idx,
                        "chunk_count_in_section": total,
                        "char_count": len(part),
                    },
                }
            )

    if isinstance(data, list):
        for i, item in enumerate(data):
            body = json.dumps(item, ensure_ascii=False, indent=2)
            add_section(f"item_{i}", 0, body)
    else:
        body = json.dumps(data, ensure_ascii=False, indent=2)
        add_section("document", 0, body)

    return rows


def ingest_documents(
    *,
    repo_root: Path | None = None,
    max_chars: int = 1200,
    overlap: int = 120,
) -> dict[str, Any]:
    """
    Load markdown/json from `<repo>/data/raw`, normalize, chunk, and return a JSON-serializable payload.
    """
    root = repo_root or _repo_root()
    raw = root / "data" / "raw"
    files = _list_source_files(raw)
    rows: list[dict[str, Any]] = []

    for path in files:
        ct = path.stem
        if path.suffix.lower() == ".md":
            rows.extend(_ingest_markdown(path, ct, max_chars=max_chars, overlap=overlap))
        elif path.suffix.lower() == ".json":
            rows.extend(_ingest_json(path, ct, max_chars=max_chars, overlap=overlap))

    chunks: list[dict[str, Any]] = []
    for i, row in enumerate(rows, start=1):
        chunks.append(
            {
                "id": f"{row['content_type']}_{i:05d}",
                "content_type": row["content_type"],
                "source_file": row["source_file"],
                "section_title": row["section_title"],
                "section_level": row["section_level"],
                "text": row["text"],
                "metadata": row["metadata"],
            }
        )

    return {
        "version": 1,
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "repo_root": str(root),
        "raw_dir": str(raw),
        "sources": sorted({p.name for p in files}),
        "chunk_count": len(chunks),
        "ingest_options": {"max_chars": max_chars, "overlap": overlap},
        "chunks": chunks,
    }


def write_chunks_json(
    payload: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_ingestion(
    *,
    repo_root: Path | None = None,
    output_path: Path | None = None,
    max_chars: int = 1200,
    overlap: int = 120,
) -> Path:
    root = repo_root or _repo_root()
    out = output_path or (root / "data" / "processed" / "chunks.json")
    payload = ingest_documents(repo_root=root, max_chars=max_chars, overlap=overlap)
    write_chunks_json(payload, out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest data/raw into data/processed/chunks.json")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: parent of backend/ or INGEST_REPO_ROOT)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path (default: <repo>/data/processed/chunks.json)",
    )
    parser.add_argument("--max-chars", type=int, default=1200, help="Soft max characters per chunk")
    parser.add_argument("--overlap", type=int, default=120, help="Overlap for hard-split windows")
    args = parser.parse_args()

    root = args.repo_root.resolve() if args.repo_root else None
    out = run_ingestion(
        repo_root=root,
        output_path=args.output.resolve() if args.output else None,
        max_chars=args.max_chars,
        overlap=args.overlap,
    )
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
