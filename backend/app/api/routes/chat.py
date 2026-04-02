"""
Chat API route with optional audio synthesis.

Handles Q&A with RAG retrieval. If include_tts=True, attempts to synthesize answer audio.
Graceful fallback: if TTS fails, text response is still returned (audio=None).
"""

import json
import logging
import time

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.core.config import get_settings
from app.rag.retrieve import retrieve_top_k
from app.schemas.chat import ChatRequest, ChatResponse, RetrievalHitSchema, SourceCitation
from app.services import llm_service
from app.services.llm_service import GroundedAnswerResult
from app.services.session_store import get_session_store
from app.services.voice_service import VoiceOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


def _benchmark_requested(request: Request) -> bool:
    return request.headers.get("x-benchmark", "").lower() in ("1", "true", "yes")


@router.post("/chat", response_model=None)
async def chat(request: Request, body: ChatRequest) -> JSONResponse:
    """
    Answer a question with RAG-grounded response.
    
    Args:
        body: ChatRequest with question, optional session_id, optional include_tts
        
    Returns:
        ChatResponse with answer, sources, and optional audio metadata
        
    Note:
        - Text response is always returned (primary)
        - Audio is optional (attempts synthesis if include_tts=True)
        - If TTS fails, audio=None; text still works
    """
    settings = get_settings()
    store = get_session_store(settings.session_max_messages, settings.session_max_total_chars)
    session_id = store.ensure_session(body.session_id)
    history_text = store.get_history_text(session_id)

    t0 = time.perf_counter()
    hits, err = retrieve_top_k(body.question, settings=settings)
    t_retrieval = time.perf_counter()

    result = await llm_service.generate_grounded_answer(
        body.question,
        session_id,
        retrieval_hits=hits,
        retrieval_error=err,
        settings=settings,
        conversation_history=history_text or None,
    )
    t_llm = time.perf_counter()
    logger.info(
        "chat_timing retrieval_s=%.3f llm_s=%.3f total_to_answer_s=%.3f",
        t_retrieval - t0,
        t_llm - t_retrieval,
        t_llm - t0,
    )

    store.append_turn(session_id, "user", body.question)
    store.append_turn(session_id, "assistant", result.answer)

    audio_metadata = None
    tts_error: str | None = None
    if body.include_tts:
        audio_metadata, tts_error = await VoiceOrchestrator.synthesize_answer_audio(result.answer, settings)

    payload = ChatResponse(
        answer=result.answer,
        confidence=result.confidence,
        grounding_note=result.grounding_note,
        sources=[
            SourceCitation(excerpt=c.excerpt)
            for c in result.citations
        ],
        session_id=session_id,
        audio=audio_metadata,
        tts_error=tts_error,
        retrieval=[RetrievalHitSchema(**h.to_api_dict()) for h in hits],
        retrieval_error=err,
    ).model_dump()

    headers: dict[str, str] = {}
    if _benchmark_requested(request):
        headers["X-Benchmark-Retrieval-S"] = f"{t_retrieval - t0:.6f}"
        headers["X-Benchmark-Llm-S"] = f"{t_llm - t_retrieval:.6f}"
        headers["X-Benchmark-Chat-Total-S"] = f"{t_llm - t0:.6f}"

    return JSONResponse(content=payload, headers=headers)


async def _stream_terminal_payload(
    *,
    body: ChatRequest,
    session_id: str,
    result: GroundedAnswerResult,
    hits,
    err: str | None,
    settings,
) -> dict:
    """Build terminal SSE JSON (same fields as POST /api/chat plus done: true)."""
    audio_metadata = None
    tts_error: str | None = None
    if body.include_tts:
        audio_metadata, tts_error = await VoiceOrchestrator.synthesize_answer_audio(
            result.answer, settings
        )

    payload = ChatResponse(
        answer=result.answer,
        confidence=result.confidence,
        grounding_note=result.grounding_note,
        sources=[SourceCitation(excerpt=c.excerpt) for c in result.citations],
        session_id=session_id,
        audio=audio_metadata,
        tts_error=tts_error,
        retrieval=[RetrievalHitSchema(**h.to_api_dict()) for h in hits],
        retrieval_error=err,
    ).model_dump()
    payload["done"] = True
    return payload


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest):
    """Stream tokens, then one terminal event with full ChatResponse (sources, retrieval, optional TTS)."""
    settings = get_settings()
    store = get_session_store(settings.session_max_messages, settings.session_max_total_chars)
    session_id = store.ensure_session(body.session_id)
    history_text = store.get_history_text(session_id)

    hits, err = retrieve_top_k(body.question, settings=settings)

    store.append_turn(session_id, "user", body.question)

    async def generate():
        try:
            if err:
                ans = f"I can't answer right now: {err}"
                store.append_turn(session_id, "assistant", ans)
                early = ChatResponse(
                    answer=ans,
                    confidence="low",
                    grounding_note=None,
                    sources=[],
                    session_id=session_id,
                    audio=None,
                    tts_error=None,
                    retrieval=[RetrievalHitSchema(**h.to_api_dict()) for h in hits],
                    retrieval_error=err,
                ).model_dump()
                early["done"] = True
                yield f"data: {json.dumps(early)}\n\n"
                return

            if not hits:
                ans = "No relevant passages found for this question."
                store.append_turn(session_id, "assistant", ans)
                early = ChatResponse(
                    answer=ans,
                    confidence="low",
                    grounding_note=None,
                    sources=[],
                    session_id=session_id,
                    audio=None,
                    tts_error=None,
                    retrieval=[],
                    retrieval_error=None,
                ).model_dump()
                early["done"] = True
                yield f"data: {json.dumps(early)}\n\n"
                return

            full_raw = ""
            async for chunk in llm_service.generate_grounded_answer_stream(
                body.question,
                session_id,
                retrieval_hits=hits,
                retrieval_error=err,
                settings=settings,
                conversation_history=history_text,
            ):
                full_raw += chunk
                yield f"data: {json.dumps({'token': chunk, 'session_id': session_id})}\n\n"

            parsed = llm_service.parse_streamed_llm_text(full_raw, hits)
            store.append_turn(session_id, "assistant", parsed.answer)
            final = await _stream_terminal_payload(
                body=body,
                session_id=session_id,
                result=parsed,
                hits=hits,
                err=err,
                settings=settings,
            )
            yield f"data: {json.dumps(final)}\n\n"

        except Exception as e:
            logger.error("Stream error: %s", e)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
