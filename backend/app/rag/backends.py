"""
Pluggable retrieval backends. Swap implementations or add a vector DB client later
by implementing the same `.search` contract as `TfidfBackend` / `OllamaBackend`.
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
            min_df=1,
            max_df=0.95,
        )
        self._matrix = self._vectorizer.fit_transform(texts)

    def search(self, query: str, k: int) -> list[RetrievalHit]:
        if not self._chunks:
            return []
        q = self._vectorizer.transform([query])
        scores = cosine_similarity(q, self._matrix).ravel()
        k = min(k, len(scores))
        top = np.argsort(-scores)[:k]
        results = [_hit(self._chunks[i], float(scores[i])) for i in top]
        
        query_lower = query.lower()
        
        # Fallback for education queries: if score is very low and query contains education keywords
        education_keywords = {'school', 'university', 'unt', 'education', 'graduate', 'graduation', 
                            'degree', 'study', 'college', 'coursework', 'gpa', 'student'}
        if results and results[0].score < 0.01 and any(keyword in query_lower for keyword in education_keywords):
            education_chunks = [
                c for c in self._chunks 
                if c.get("source_file") == "education.md"
            ]
            if education_chunks:
                results = [_hit(c, 0.5) for c in education_chunks[:k]]
                return results
        
        # Fallback for experience/work queries: boost experience.md if scores are too low
        # This handles queries like "how many years", "work experience", "tell me about yourself"
        experience_keywords = {'years', 'experience', 'work', 'role', 'employed', 'job', 'position', 
                              'duration', 'background', 'career', 'professional', 'engineer', 'avtar', 'niro'}
        if results and results[0].score < 0.2 and any(keyword in query_lower for keyword in experience_keywords):
            # Check if experience.md is in top results, if not, prioritize it
            has_experience = any(c.get("source_file") == "experience.md" for c in results)
            if not has_experience:
                experience_chunks = [
                    c for c in self._chunks 
                    if c.get("source_file") == "experience.md"
                ]
                if experience_chunks:
                    # Return mix of experience chunks and top other results
                    results = [_hit(c, 0.5) for c in experience_chunks[:k]]
                    return results
        
        return results


class OllamaBackend(RetrievalBackend):
    """Embedding + cosine similarity using local Ollama embeddings API."""

    def __init__(
        self,
        chunks: list[ChunkRecord],
        *,
        model: str,
        base_url: str,
        timeout_s: float = 120.0,
    ) -> None:
        self._chunks = chunks
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
        batch_size = 32
        with httpx.Client(timeout=self._timeout) as client:
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                vecs = self._embed_strings(client, batch)
                out.extend(vecs)
        return np.array(out, dtype=np.float64)

    def _embed_strings(self, client: httpx.Client, texts: list[str]) -> list[list[float]]:
        url = f"{self._base_url}/api/embed"
        vecs: list[list[float]] = []
        for text in texts:
            r = client.post(
                url,
                json={"model": self._model, "input": text},
            )
            r.raise_for_status()
            data = r.json()
            embedding = data.get("embedding", [])
            vecs.append(embedding)
        return vecs

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
    ollama_embed_model: str,
    ollama_base_url: str,
) -> RetrievalBackend:
    if name == "ollama":
        return OllamaBackend(
            chunks,
            model=ollama_embed_model,
            base_url=ollama_base_url,
        )
    if name == "tfidf":
        return TfidfBackend(chunks)
    raise ValueError(f"Unknown retrieval backend: {name}")
