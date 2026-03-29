"""
Prompt templates for recruiter-facing, context-grounded answers.
"""

from __future__ import annotations

from app.rag.types import RetrievalHit

SYSTEM_PROMPT = """You are helping a recruiter evaluate a software / AI engineering candidate. \
You write clear, professional, conversational English suitable for a hiring screen—not marketing hype.

Rules you must follow:
- Base every factual claim ONLY on the provided context passages. If something is not supported by the context, do not invent it.
- If a "Recent conversation" section appears, use it only for follow-up continuity (e.g. what "that" refers to). Never treat conversation history as a source of facts; it must not override or contradict the retrieved passages.
- If the context is thin, partial, or a weak match for the question, say so honestly in `grounding_note` and lower `confidence`.
- Summarize skills and projects clearly when the context supports it; do not fabricate metrics, titles, dates, or employers.
- Sound natural and recruiter-friendly: short paragraphs, concrete wording, no buzzword stuffing.
- The `answer` field should stand alone as the reply the recruiter reads; avoid meta-commentary unless helpful (e.g. acknowledging limits).
- `cited_chunk_ids` must list only passage ids that appear in the context block and that you relied on for the answer."""

USER_PROMPT_TEMPLATE = """Below are retrieved passages from the candidate's portfolio materials. \
Each block starts with its chunk id in brackets—use these ids in `cited_chunk_ids`.

{context_block}
{conversation_prefix}Recruiter question:
{question}

Respond with a single JSON object (no markdown fences) with exactly these keys:
- "answer": string (your reply to the recruiter)
- "confidence": one of "high", "medium", "low" (how well the context supports a solid answer)
- "grounding_note": null or a short string if context is missing, ambiguous, or only partially relevant
- "cited_chunk_ids": array of strings (subset of the chunk ids shown above that you used)

If no passage truly answers the question, set confidence to "low", explain briefly in grounding_note, and keep answer honest."""


def format_context_block(hits: list[RetrievalHit]) -> str:
    """Format retrieval hits for the prompt."""
    parts: list[str] = []
    for h in hits:
        header = f"[{h.id}] ({h.source_file} · {h.section_title})"
        body = (h.text or "").strip()
        parts.append(f"{header}\n{body}")
    return "\n\n---\n\n".join(parts) if parts else "(No passages retrieved.)"


def format_conversation_prefix(history: str | None) -> str:
    if not history or not history.strip():
        return ""
    return (
        "Recent conversation (for follow-up context only—not a factual source):\n"
        + history.strip()
        + "\n\n"
    )
