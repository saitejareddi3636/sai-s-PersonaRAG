"""
Pluggable retrieval backends. Swap implementations or add a vector DB client later
by implementing the same `.search` contract as `TfidfBackend` / `OpenAIBackend`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.rag.types import ChunkRecord, RetrievalHit


class RetrievalBackend(ABC):
    @abstractmethod
    def search(self, query: str, k: int) -> list[RetrievalHit]:
        raise NotImplementedError


class TfidfBackend(RetrievalBackend):
    """Keyword-oriented retrieval using TF–IDF + cosine similarity (no external API)."""

    def __init__(
        self,
        chunks: list[ChunkRecord],
        *,
        max_features: int = 8192,
    ) -> None:
        self._chunks = chunks
        texts = [c["text"] for c in chunks]
        self._vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self._matrix = self._vectorizer.fit_transform(texts)

    def search(self, query: str, k: int) -> list[RetrievalHit]:
        if not self._chunks:
            return []
        q = self._vectorizer.transform([query])
        scores = cosine_similarity(q, self._matrix).ravel()
        k = min(k, len(scores))
        top = np.argsort(-scores)[:k]
        return [_hit(self._chunks[i], float(scores[i])) for i in top]


class OpenAIBackend(RetrievalBackend):
    """Embedding + cosine similarity using the OpenAI embeddings HTTP API."""

    def __init__(
        self,
        chunks: list[ChunkRecord],
        *,
        api_key: str,
        model: str,
        base_url: str,
        timeout_s: float = 120.0,
    ) -> None:
        self._chunks = chunks
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_s
        texts = [c["text"] for c in chunks]
        self._doc_matrix = self._embed_batch(texts)
        self._doc_matrix = _l2_normalize_rows(self._doc_matrix)

    def _embed_batch(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0))
        out: list[list[float]] = []
        batch_size = 64
        with httpx.Client(timeout=self._timeout) as client:
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                vecs = self._embed_strings(client, batch)
                out.extend(vecs)
        return np.array(out, dtype=np.float64)

    def _embed_strings(self, client: httpx.Client, texts: list[str]) -> list[list[float]]:
        url = f"{self._base_url}/embeddings"
        r = client.post(
            url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={"model": self._model, "input": texts},
        )
        r.raise_for_status()
        data = r.json()["data"]
        ordered = sorted(data, key=lambda d: d["index"])
        return [item["embedding"] for item in ordered]

    def search(self, query: str, k: int) -> list[RetrievalHit]:
        if not self._chunks:
            return []
        with httpx.Client(timeout=self._timeout) as client:
            qmat = self._embed_strings(client, [query])
        q = _l2_normalize_rows(np.array(qmat, dtype=np.float64))
        scores = (self._doc_matrix @ q.T).ravel()
        k = min(k, len(scores))
        top = np.argsort(-scores)[:k]
        return [_hit(self._chunks[i], float(scores[i])) for i in top]


def _l2_normalize_rows(m: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return m / norms


def _hit(chunk: ChunkRecord, score: float) -> RetrievalHit:
    meta = dict(chunk.get("metadata") or {})
    return RetrievalHit(
        id=chunk["id"],
        score=score,
        content_type=chunk["content_type"],
        source_file=chunk["source_file"],
        section_title=chunk["section_title"],
        section_level=int(chunk.get("section_level", 0)),
        text=chunk["text"],
        metadata=meta,
    )


def build_backend(
    name: str,
    chunks: list[ChunkRecord],
    *,
    openai_api_key: str | None,
    openai_embedding_model: str,
    openai_base_url: str,
) -> RetrievalBackend:
    key = (openai_api_key or "").strip()
    if name == "openai":
        if not key:
            raise ValueError("OPENAI_API_KEY is required when RETRIEVAL_BACKEND=openai")
        return OpenAIBackend(
            chunks,
            api_key=key,
            model=openai_embedding_model,
            base_url=openai_base_url,
        )
    if name == "tfidf":
        return TfidfBackend(chunks)
    raise ValueError(f"Unknown retrieval backend: {name}")
