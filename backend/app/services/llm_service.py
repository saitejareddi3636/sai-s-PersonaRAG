from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Literal

import httpx

from app.core.config import Settings
from app.rag.types import RetrievalHit
from app.services.prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    format_context_block,
    format_conversation_prefix,
)

logger = logging.getLogger(__name__)

ConfidenceLevel = Literal["high", "medium", "low"]


@dataclass
class Citation:
    chunk_id: str
    source_file: str
    section_title: str
    content_type: str
    score: float
    excerpt: str


@dataclass
class GroundedAnswerResult:
    answer: str
    confidence: ConfidenceLevel
    grounding_note: str | None
    citations: list[Citation]


def _weak_retrieval_signal(hits: list[RetrievalHit], settings: Settings) -> bool:
    if not hits:
        return True
    best = max(h.score for h in hits)
    return best < settings.retrieval_weak_score_threshold


async def generate_grounded_answer(
    question: str,
    session_id: str | None,
    *,
    retrieval_hits: list[RetrievalHit],
    retrieval_error: str | None,
    settings: Settings,
    conversation_history: str | None = None,
) -> GroundedAnswerResult:
    _ = session_id
    q = question.strip()

    if retrieval_error:
        return GroundedAnswerResult(
            answer=(
                "I can't ground an answer right now because the portfolio index isn't available. "
                f"Details: {retrieval_error}"
            ),
            confidence="low",
            grounding_note="Retrieval/index error; no passages loaded.",
            citations=[],
        )

    if not retrieval_hits:
        return GroundedAnswerResult(
            answer=(
                "I don't have enough indexed material to answer that yet. "
                "Try rephrasing, or ensure portfolio content has been ingested into chunks."
            ),
            confidence="low",
            grounding_note="No relevant passages were retrieved for this question.",
            citations=[],
        )

    api_key = (settings.openai_api_key or "").strip()
    if not api_key:
        return _fallback_without_llm(q, retrieval_hits, settings, conversation_history=conversation_history)

    context_block = format_context_block(retrieval_hits)
    conv = format_conversation_prefix(conversation_history)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        context_block=context_block,
        conversation_prefix=conv,
        question=q,
    )
    if _weak_retrieval_signal(retrieval_hits, settings):
        user_prompt += (
            "\n\nNote: retrieval scores suggest only a partial match—prefer confidence "
            '"medium" or "low" and explain limitations in grounding_note if appropriate.'
        )

    try:
        payload = await _call_openai_chat(
            api_key=api_key,
            base_url=settings.openai_base_url,
            model=settings.openai_chat_model,
            system=SYSTEM_PROMPT,
            user=user_prompt,
        )
        return _parse_llm_payload(payload, retrieval_hits)
    except Exception as e:
        logger.exception("OpenAI chat failed: %s", e)
        return _fallback_without_llm(
            q,
            retrieval_hits,
            settings,
            extra_note=f"LLM request failed ({e!s}); showing excerpt-based fallback.",
            conversation_history=conversation_history,
        )


def _fallback_without_llm(
    question: str,
    hits: list[RetrievalHit],
    settings: Settings,
    extra_note: str | None = None,
    conversation_history: str | None = None,
) -> GroundedAnswerResult:
    """Honest excerpt-style summary when no API key or LLM failure."""
    cites = [_hit_to_citation(h) for h in hits[:5]]
    parts = [
        "Here is what the indexed portfolio passages contain that is closest to your question "
        f'("{question}"). A full LLM summary is not configured (set OPENAI_API_KEY) or the model request failed.'
    ]
    if conversation_history and conversation_history.strip():
        clip = conversation_history.strip()
        if len(clip) > 1200:
            clip = clip[:1200] + "…"
        parts.insert(1, f"Recent thread (continuity only, not a data source):\n{clip}")
    if extra_note:
        parts.append(extra_note)
    for h in hits[:3]:
        preview = h.text.strip().replace("\n", " ")
        if len(preview) > 320:
            preview = preview[:320] + "…"
        parts.append(f"• [{h.source_file} · {h.section_title}]: {preview}")
    conf: ConfidenceLevel = "medium" if hits else "low"
    if _weak_retrieval_signal(hits, settings):
        conf = "low"
    gn = extra_note or "Excerpt-only mode without LLM synthesis."
    return GroundedAnswerResult(
        answer="\n\n".join(parts),
        confidence=conf,
        grounding_note=gn,
        citations=cites,
    )


def _hit_to_citation(h: RetrievalHit) -> Citation:
    excerpt = h.text.strip().replace("\n", " ")
    if len(excerpt) > 200:
        excerpt = excerpt[:200] + "…"
    return Citation(
        chunk_id=h.id,
        source_file=h.source_file,
        section_title=h.section_title,
        content_type=h.content_type,
        score=h.score,
        excerpt=excerpt,
    )


async def _call_openai_chat(
    *,
    api_key: str,
    base_url: str,
    model: str,
    system: str,
    user: str,
) -> dict[str, object]:
    url = f"{base_url.rstrip('/')}/chat/completions"
    body = {
        "model": model,
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=body,
        )
        r.raise_for_status()
        data = r.json()
    content = data["choices"][0]["message"]["content"]
    if not isinstance(content, str):
        raise ValueError("Unexpected chat response shape")
    return _parse_json_loose(content)


def _parse_json_loose(raw: str) -> dict[str, object]:
    raw = raw.strip()
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        raw = m.group(0)
    return json.loads(raw)


def _parse_llm_payload(data: dict[str, object], hits: list[RetrievalHit]) -> GroundedAnswerResult:
    answer = str(data.get("answer") or "").strip()
    conf_raw = str(data.get("confidence") or "medium").lower()
    if conf_raw not in ("high", "medium", "low"):
        conf_raw = "medium"
    confidence: ConfidenceLevel = conf_raw  # type: ignore[assignment]
    gn = data.get("grounding_note")
    grounding_note = str(gn).strip() if gn is not None and str(gn).strip() else None

    ids_raw = data.get("cited_chunk_ids")
    cited_ids: list[str] = []
    if isinstance(ids_raw, list):
        cited_ids = [str(x) for x in ids_raw if x is not None]

    by_id = {h.id: h for h in hits}
    citations: list[Citation] = []
    for cid in cited_ids:
        if cid in by_id:
            citations.append(_hit_to_citation(by_id[cid]))
    if not citations and hits:
        citations.append(_hit_to_citation(hits[0]))

    if not answer:
        answer = "I could not produce a grounded reply from the model output; please try again."

    return GroundedAnswerResult(
        answer=answer,
        confidence=confidence,
        grounding_note=grounding_note,
        citations=citations,
    )
