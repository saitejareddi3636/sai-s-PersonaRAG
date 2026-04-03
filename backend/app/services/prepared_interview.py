"""
Fast path for common recruiter / behavioral questions.

If the user message matches a prepared prompt (fuzzy), return the canned answer
immediately — no Ollama call. Edit backend/data/prepared_interview.json to add
or change entries (prompts + answer text).
"""

from __future__ import annotations

import json
import logging
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# backend/app/services -> backend/data
_DEFAULT_JSON = Path(__file__).resolve().parents[2] / "data" / "prepared_interview.json"

_cache: list[dict[str, Any]] | None = None


def _normalize(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[\s\n\r\t]+", " ", s)
    s = re.sub(r"[^\w\s?']", "", s)
    return s


def _load_items() -> list[dict[str, Any]]:
    global _cache
    if _cache is not None:
        return _cache
    path = _DEFAULT_JSON
    if not path.is_file():
        _cache = []
        return _cache
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            _cache = []
            return _cache
        _cache = [x for x in raw if isinstance(x, dict) and (x.get("answer") or "").strip()]
        return _cache
    except Exception as e:
        logger.warning("prepared_interview: could not load %s: %s", path, e)
        _cache = []
        return _cache


def reload_prepared_interview_cache() -> None:
    """Tests / hot reload."""
    global _cache
    _cache = None
    _load_items()


def match_prepared_answer(question: str, *, min_ratio: float = 0.62) -> str | None:
    """
    Return a prepared answer if question matches one of the prompt variants.

    Uses: (1) substring containment for long prompts, (2) best SequenceMatcher ratio.
    """
    u = _normalize(question)
    if len(u) < 6:
        return None

    items = _load_items()
    best_answer: str | None = None
    best_score = 0.0

    for item in items:
        prompts = item.get("prompts")
        if not isinstance(prompts, list):
            continue
        answer = str(item.get("answer", "")).strip()
        if not answer:
            continue

        for p in prompts:
            pn = _normalize(str(p))
            if len(pn) < 8:
                continue
            # Strong: user question contains the canonical prompt (or vice versa)
            if len(pn) >= 18 and (pn in u or u in pn):
                return answer
            ratio = SequenceMatcher(None, u, pn).ratio()
            # Shorter prompts need higher overlap
            adj = ratio if len(pn) > 24 else ratio * 0.95
            if adj > best_score:
                best_score = adj
                best_answer = answer

    if best_score >= min_ratio and best_answer:
        return best_answer
    return None
