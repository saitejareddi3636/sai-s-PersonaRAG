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

_OLLAMA_HTTP_CLIENT: httpx.AsyncClient | None = None


def _get_ollama_http_client() -> httpx.AsyncClient:
    """Reuse one async HTTP client to avoid repeated connection setup overhead."""
    global _OLLAMA_HTTP_CLIENT
    if _OLLAMA_HTTP_CLIENT is None:
        _OLLAMA_HTTP_CLIENT = httpx.AsyncClient(timeout=120.0)
    return _OLLAMA_HTTP_CLIENT

ConfidenceLevel = Literal["high", "medium", "low"]
SOCIAL_QUERIES = {
    "hi",
    "hello",
    "hey",
    "hey there",
    "howdy",
    "greetings",
}
OUT_OF_SCOPE_REPLY = "I don't have specific info about that. Please contact Sai directly."
PROFILE_QUERY_KEYWORDS = {
    "you",
    "your",
    "yourself",
    "background",
    "experience",
    "work",
    "worked",
    "company",
    "role",
    "skills",
    "projects",
    "degree",
    "gpa",
    "graduate",
    "availability",
    "join",
    "location",
    "resume",
    "rag",
    "llm",
    "docker",
    "kubernetes",
    "ci/cd",
    "framework",
    "coursework",
}
AVAILABILITY_KEYWORDS = (
    "availability",
    "when can you join",
    "when can you start",
    "joining",
    "start date",
)


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


def _is_social_query(question: str) -> bool:
    q = question.strip().lower()
    return q in SOCIAL_QUERIES


def _social_response(question: str) -> str:
    q = question.strip().lower()
    if q == "hey there":
        return "Hey there! Happy to help with any question about my background."
    return "Hello! Happy to help with any question about my background."


def _is_profile_query(question: str) -> bool:
    q = question.strip().lower()
    return any(k in q for k in PROFILE_QUERY_KEYWORDS)


def _is_availability_query(question: str) -> bool:
    q = question.strip().lower()
    return any(k in q for k in AVAILABILITY_KEYWORDS)


def _availability_from_hits(hits: list[RetrievalHit]) -> str | None:
    text = " ".join(h.text for h in hits[:5]).lower()
    has_grad = "graduat" in text
    has_location = any(k in text for k in ("remote", "hybrid", "on-site", "onsite"))
    has_new_grad = "new grad" in text or "entry-level" in text
    if has_grad or has_location or has_new_grad:
        parts: list[str] = []
        if has_new_grad:
            parts.append("I'm actively recruiting for new grad and entry-level roles.")
        if has_grad:
            parts.append("I'm graduating in May 2026.")
        if has_location:
            parts.append("I'm open to remote, on-site, or hybrid opportunities in the US.")
        return " ".join(parts).strip()
    return None


def _duration_answer(question: str, hits: list[RetrievalHit]) -> str | None:
    q = question.lower()
    role = None
    if "avtar" in q:
        role = "avtar"
    elif "niro" in q:
        role = "niro"
    if not role:
        return None
    role_text = " ".join(h.text for h in hits if role in h.text.lower())
    all_text = " ".join(h.text for h in hits)
    m = re.search(r"Duration:\s*([A-Za-z]{3}\s*\d{4}\s*[–-]\s*[A-Za-z]{3}\s*\d{4})", role_text)
    if not m:
        m = re.search(
            rf"{role}[^.()]*\(([A-Za-z]{{3}}\s*\d{{4}}\s*(?:to|–|-)\s*[A-Za-z]{{3}}\s*\d{{4}})\)",
            all_text,
            flags=re.IGNORECASE,
        )
    if not m:
        all_ranges = re.findall(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}\s*(?:to|–|-)\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}", all_text, flags=re.IGNORECASE)
        if all_ranges:
            return f"I worked at {role.title()} from {all_ranges[0].replace('–', ' to ').replace('-', ' to ')}."
        return None
    span = m.group(1).replace("–", " to ").replace("-", " to ")
    return f"I worked at {role.title()} from {span}."


def _weak_retrieval_signal(hits: list[RetrievalHit], settings: Settings) -> bool:
    if not hits:
        return True
    best = max(h.score for h in hits)
    return best < settings.retrieval_weak_score_threshold


def _extract_keyword_sentence(hits: list[RetrievalHit], keywords: tuple[str, ...]) -> str | None:
    for h in hits[:8]:
        lines = [ln.strip() for ln in h.text.splitlines() if ln.strip()]
        for ln in lines:
            lower = ln.lower()
            if any(k in lower for k in keywords):
                return ln.lstrip("- ").strip()
    return None


def _fact_answer_from_hits(question: str, hits: list[RetrievalHit]) -> str | None:
    q = question.lower()
    if "rag" in q:
        s = _extract_keyword_sentence(hits, ("rag", "retrieval-augmented generation"))
        return s or None
    if "docker" in q:
        s = _extract_keyword_sentence(hits, ("docker", "docker compose", "container"))
        return s or None
    if "backend framework" in q:
        vals = []
        text = " ".join(h.text for h in hits[:8]).lower()
        if "fastapi" in text:
            vals.append("FastAPI")
        if "spring boot" in text:
            vals.append("Spring Boot")
        if vals:
            return "I have used " + " and ".join(vals) + " for backend development."
        return None
    if "coursework" in q:
        s = _extract_keyword_sentence(hits, ("coursework", "data structures", "algorithms", "system design"))
        return s or None
    if "kubernetes" in q:
        s = _extract_keyword_sentence(hits, ("kubernetes",))
        return s or None
    if "type of company" in q or "company are you looking for" in q:
        lines = []
        for h in hits[:8]:
            for ln in [x.strip().lstrip("- ").strip() for x in h.text.splitlines() if x.strip()]:
                low = ln.lower()
                if any(t in low for t in ("companies building ai", "backend-focused teams", "startups", "prioritizing production reliability", "learning opportunities")):
                    lines.append(ln)
        if lines:
            return "I am looking for " + "; ".join(lines[:3]) + "."
        return None
    return None


def _is_strict_fact_query(question: str) -> bool:
    q = question.lower()
    return any(
        k in q
        for k in (
            "rag experience",
            "experience with docker",
            "experience with kubernetes",
            "backend frameworks",
            "backend framework",
            "coursework",
            "how long did you work",
            "how long were you",
            "what are your growth areas",
        )
    )


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

    if _is_social_query(q):
        return GroundedAnswerResult(
            answer=_social_response(q),
            confidence="high",
            grounding_note=None,
            citations=[],
        )
    if _is_availability_query(q):
        extracted = _availability_from_hits(retrieval_hits)
        if extracted:
            return GroundedAnswerResult(
                answer=extracted,
                confidence="high",
                grounding_note=None,
                citations=[_hit_to_citation(h) for h in retrieval_hits[:2]],
            )
        return GroundedAnswerResult(
            answer=OUT_OF_SCOPE_REPLY,
            confidence="low",
            grounding_note="Availability details not clearly present in retrieved passages.",
            citations=[],
        )
    if "how long did you work" in q or "how long were you" in q:
        duration = _duration_answer(q, retrieval_hits)
        if duration:
            return GroundedAnswerResult(
                answer=duration,
                confidence="high",
                grounding_note=None,
                citations=[_hit_to_citation(h) for h in retrieval_hits[:2]],
            )
    factual = _fact_answer_from_hits(q, retrieval_hits)
    if factual:
        return GroundedAnswerResult(
            answer=factual,
            confidence="high",
            grounding_note=None,
            citations=[_hit_to_citation(h) for h in retrieval_hits[:2]],
        )
    if _is_strict_fact_query(q):
        return GroundedAnswerResult(
            answer=OUT_OF_SCOPE_REPLY,
            confidence="low",
            grounding_note="No clear grounded fact was found for this specific question.",
            citations=[],
        )

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
            answer=OUT_OF_SCOPE_REPLY,
            confidence="low",
            grounding_note="No relevant passages were retrieved for this question.",
            citations=[],
        )
    if _weak_retrieval_signal(retrieval_hits, settings) and not _is_profile_query(q):
        return GroundedAnswerResult(
            answer=OUT_OF_SCOPE_REPLY,
            confidence="low",
            grounding_note="Question appears out of scope for candidate-specific materials.",
            citations=[],
        )

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
        payload = await _call_ollama_chat(
            base_url=settings.ollama_base_url,
            model=settings.ollama_chat_model,
            system=SYSTEM_PROMPT,
            user=user_prompt,
            keep_alive=settings.ollama_keep_alive,
        )
        return _parse_llm_payload(payload, retrieval_hits)
    except Exception as e:
        logger.exception("Ollama chat failed: %s", e)
        return _fallback_without_llm(
            q,
            retrieval_hits,
            settings,
            extra_note=f"LLM request failed ({e!s}); showing excerpt-based fallback.",
            conversation_history=conversation_history,
        )


async def generate_grounded_answer_stream(
    question: str,
    session_id: str | None,
    *,
    retrieval_hits: list[RetrievalHit],
    retrieval_error: str | None,
    settings: Settings,
    conversation_history: str | None = None,
):
    """Stream answer tokens as they arrive."""
    _ = session_id
    q = question.strip()

    if _is_social_query(q):
        yield _social_response(q)
        return

    if retrieval_error or not retrieval_hits:
        fallback = await generate_grounded_answer(
            question, session_id,
            retrieval_hits=retrieval_hits,
            retrieval_error=retrieval_error,
            settings=settings,
            conversation_history=conversation_history,
        )
        yield fallback.answer
        return

    context_block = format_context_block(retrieval_hits)
    conv = format_conversation_prefix(conversation_history)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        context_block=context_block,
        conversation_prefix=conv,
        question=q,
    )

    try:
        buffer = ""
        async for chunk in _call_ollama_chat_stream(
            base_url=settings.ollama_base_url,
            model=settings.ollama_chat_model,
            system=SYSTEM_PROMPT,
            user=user_prompt,
            keep_alive=settings.ollama_keep_alive,
        ):
            msg = chunk.get("message", {}).get("content", "")
            if msg:
                buffer += msg
                yield msg
    except Exception as e:
        logger.exception("Stream error: %s", e)
        yield f" [Error: {e}]"


def _fallback_without_llm(
    question: str,
    hits: list[RetrievalHit],
    settings: Settings,
    extra_note: str | None = None,
    conversation_history: str | None = None,
) -> GroundedAnswerResult:
    """Honest excerpt-style summary when LLM fails."""
    cites = [_hit_to_citation(h) for h in hits[:5]]
    parts = [
        "Here is what the indexed portfolio passages contain that is closest to your question "
        f'("{question}"). A full LLM summary is not available right now (Ollama connection failed or service unavailable).'
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
    gn = extra_note or "Excerpt-only mode; LLM unavailable."
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


async def _call_ollama_chat(
    *,
    base_url: str,
    model: str,
    system: str,
    user: str,
    keep_alive: str = "15m",
) -> dict[str, object]:
    """Non-streaming chat call."""
    url = f"{base_url.rstrip('/')}/api/chat"
    body: dict[str, object] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
    }
    if keep_alive.strip():
        body["keep_alive"] = keep_alive.strip()
    client = _get_ollama_http_client()
    r = await client.post(url, json=body)
    r.raise_for_status()
    data = r.json()
    content = data.get("message", {}).get("content", "")
    if not isinstance(content, str):
        raise ValueError("Unexpected Ollama chat response shape")
    return _parse_json_loose(content)


async def _call_ollama_chat_stream(
    *,
    base_url: str,
    model: str,
    system: str,
    user: str,
    keep_alive: str = "15m",
):
    """Stream chat responses from Ollama."""
    url = f"{base_url.rstrip('/')}/api/chat"
    body: dict[str, object] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": True,
    }
    if keep_alive.strip():
        body["keep_alive"] = keep_alive.strip()
    client = _get_ollama_http_client()
    async with client.stream("POST", url, json=body) as r:
        r.raise_for_status()
        async for line in r.aiter_lines():
            if line:
                data = json.loads(line)
                yield data


def _parse_json_loose(raw: str) -> dict[str, object]:
    """Parse JSON from response, with graceful fallback."""
    raw = raw.strip()
    if not raw:
        # Empty response - return basic structure
        return {
            "answer": "[No response from model]",
            "confidence": "low",
            "grounding_note": "Model returned empty response",
            "cited_chunk_ids": [],
        }
    
    # Try to find JSON object in response
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        raw = m.group(0)
    
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            ans = parsed.get("answer")
            if isinstance(ans, str) and ans.strip().startswith("{") and '"confidence"' in ans:
                try:
                    nested = json.loads(ans)
                    if isinstance(nested, dict):
                        return nested
                except Exception:
                    pass
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        # If not JSON, wrap as plain text response
        return {
            "answer": raw[:500],  # Cap at 500 chars
            "confidence": "medium",
            "grounding_note": "Model returned plain text instead of structured response",
            "cited_chunk_ids": [],
        }


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
        answer = OUT_OF_SCOPE_REPLY
        confidence = "low"
        grounding_note = "Model output was empty."
    elif re.match(r"^i\s+don'?t?$", answer.lower()):
        answer = OUT_OF_SCOPE_REPLY
        confidence = "low"
        if grounding_note is None:
            grounding_note = "Model output was truncated; returned a grounded fallback."
    elif answer.startswith("{") and '"answer"' in answer and '"confidence"' in answer:
        answer = OUT_OF_SCOPE_REPLY
        confidence = "low"
        grounding_note = "Model returned malformed nested JSON in answer field."

    return GroundedAnswerResult(
        answer=answer,
        confidence=confidence,
        grounding_note=grounding_note,
        citations=citations,
    )


def parse_streamed_llm_text(
    full_answer: str, retrieval_hits: list[RetrievalHit]
) -> GroundedAnswerResult:
    """
    Convert accumulated /chat/stream text into structured output.
    Ollama streams a JSON object; greetings stream plain text.
    """
    raw = (full_answer or "").strip()
    if not raw:
        cites = (
            [_hit_to_citation(retrieval_hits[0])] if retrieval_hits else []
        )
        return GroundedAnswerResult(
            answer=OUT_OF_SCOPE_REPLY,
            confidence="low",
            grounding_note="Empty model output.",
            citations=cites,
        )
    if raw.startswith("{"):
        payload = _parse_json_loose(raw)
        return _parse_llm_payload(payload, retrieval_hits)
    return GroundedAnswerResult(
        answer=raw,
        confidence="high",
        grounding_note=None,
        citations=[],
    )
