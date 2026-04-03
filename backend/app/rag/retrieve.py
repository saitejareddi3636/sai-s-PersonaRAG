"""
Load `data/processed/chunks.json`, build a retrieval backend (TF–IDF or Ollama embeddings),
and search top-k chunks for a question.

Swap `TfidfBackend` / `OllamaBackend` in `backends.py` or add a new `RetrievalBackend`
implementation to point at a hosted vector DB later.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.core.config import Settings, get_settings
from app.rag.backends import RetrievalBackend, build_backend
from app.rag.paths import default_chunks_json_path
from app.rag.types import ChunkRecord, RetrievalHit

logger = logging.getLogger(__name__)


def _query_asks_employment_location(q: str) -> bool:
    """Employer questions TF–IDF often ranks poorly — we pin the work-history chunk."""
    s = (q or "").lower()
    return any(
        t in s
        for t in (
            "company",
            "work at",
            "where do you work",
            "where you work",
            "employer",
            "work for",
            "who do you work",
            "currently work",
            "full-time job",
        )
    )


def _pin_work_history_chunk(
    hits: list[RetrievalHit], top_k: int, settings: Settings
) -> list[RetrievalHit]:
    try:
        path = resolve_chunks_path(settings)
        chunks = load_processed_chunks(path)
    except Exception:
        return hits
    pin: ChunkRecord | None = None
    for c in chunks:
        st = (c.get("section_title") or "").lower()
        if "where i work" in st:
            pin = c
            break
    if pin is None:
        return hits
    pin_id = str(pin.get("id") or "")
    ph = RetrievalHit(
        id=pin_id,
        score=1.0,
        content_type=str(pin.get("content_type") or "unknown"),
        source_file=str(pin.get("source_file") or ""),
        section_title=str(pin.get("section_title") or ""),
        section_level=int(pin.get("section_level") or 0),
        text=str(pin.get("text") or ""),
        metadata=dict(pin.get("metadata") or {}),
    )
    rest = [h for h in hits if h.id != pin_id]
    return [ph, *rest][:top_k]


_backend: RetrievalBackend | None = None
_backend_error: str | None = None


def reset_retrieval_index() -> None:
    """Clear cached backend (tests or reload)."""
    global _backend, _backend_error
    _backend = None
    _backend_error = None


def resolve_chunks_path(settings: Settings) -> Path:
    if settings.chunks_json_path:
        return Path(settings.chunks_json_path).expanduser().resolve()
    return default_chunks_json_path()


def load_processed_chunks(path: Path) -> list[ChunkRecord]:
    if not path.is_file():
        raise FileNotFoundError(f"Chunks file not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    chunks = raw.get("chunks")
    if not isinstance(chunks, list):
        raise ValueError("chunks.json must contain a 'chunks' array")
    out: list[ChunkRecord] = []
    for i, c in enumerate(chunks):
        if not isinstance(c, dict):
            continue
        cid = c.get("id") or f"chunk_{i}"
        text = (c.get("text") or "").strip()
        if not text:
            continue
        out.append(
            {
                "id": str(cid),
                "content_type": str(c.get("content_type") or "unknown"),
                "source_file": str(c.get("source_file") or ""),
                "section_title": str(c.get("section_title") or ""),
                "section_level": int(c.get("section_level") or 0),
                "text": text,
                "metadata": dict(c.get("metadata") or {}),
            }
        )
    return out


def embed_and_index_chunks(chunks: list[ChunkRecord], settings: Settings) -> RetrievalBackend:
    """Build an in-memory index from chunk records (TF–IDF or Ollama embeddings per settings)."""
    mode = (settings.retrieval_backend or "auto").strip().lower()
    if mode == "auto":
        mode = "ollama"
    if mode not in ("tfidf", "ollama"):
        raise ValueError(f"Invalid RETRIEVAL_BACKEND: {settings.retrieval_backend}")

    logger.info(
        "Building retrieval index: mode=%s chunks=%s",
        mode,
        len(chunks),
    )
    return build_backend(
        mode,
        chunks,
        ollama_embed_model=settings.ollama_embed_model,
        ollama_base_url=settings.ollama_base_url,
    )


def get_retrieval_backend(settings: Settings | None = None) -> tuple[RetrievalBackend | None, str | None]:
    """
    Lazy singleton. Returns (backend, error_message).
    If chunks are missing or invalid, backend is None and error_message explains why.
    """
    global _backend, _backend_error
    if _backend is not None:
        return _backend, None
    if _backend_error is not None:
        return None, _backend_error

    cfg = settings or get_settings()
    try:
        path = resolve_chunks_path(cfg)
        chunks = load_processed_chunks(path)
        if not chunks:
            msg = f"No non-empty chunks in {path}; run ingestion first."
            _backend_error = msg
            logger.warning(msg)
            return None, msg
        _backend = embed_and_index_chunks(chunks, cfg)
        return _backend, None
    except FileNotFoundError as e:
        _backend_error = str(e)
        logger.warning("Retrieval disabled: %s", e)
        return None, str(e)
    except Exception as e:
        _backend_error = str(e)
        logger.exception("Retrieval index failed")
        return None, str(e)


def retrieve_top_k(question: str, k: int | None = None, settings: Settings | None = None) -> tuple[list[RetrievalHit], str | None]:
    """
    Return (hits, error). Error is set when the index could not be built or searched.
    """
    cfg = settings or get_settings()
    top_k = k if k is not None else cfg.retrieval_top_k
    top_k = max(1, min(int(top_k), 200))
    backend, err = get_retrieval_backend(cfg)
    if backend is None:
        return [], err
    q = (question or "").strip()
    if not q:
        return [], "Empty question"
    hits = backend.search(q, top_k)
    if _query_asks_employment_location(q):
        hits = _pin_work_history_chunk(hits, top_k, cfg)
    return hits, None


def warm_retrieval_index(settings: Settings | None = None) -> None:
    """Eager-load the backend (e.g. from FastAPI startup)."""
    get_retrieval_backend(settings)


# Backwards-compatible name used earlier in the project
def retrieve_relevant_chunks(query: str, top_k: int = 5) -> list[str]:
    hits, _ = retrieve_top_k(query, k=top_k)
    return [h.text for h in hits]
