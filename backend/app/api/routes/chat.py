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
from app.schemas.chat import AudioMetadata, ChatRequest, ChatResponse, RetrievalHitSchema, SourceCitation
from app.services import llm_service
from app.services.session_store import get_session_store
from app.services.tts_service import get_tts_backend

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
        audio_metadata, tts_error = await _synthesize_answer_audio(result.answer, settings)

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


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest):
    """Stream answer tokens as they arrive (faster perceived response)."""
    settings = get_settings()
    store = get_session_store(settings.session_max_messages, settings.session_max_total_chars)
    session_id = store.ensure_session(body.session_id)
    history_text = store.get_history_text(session_id)

    hits, err = retrieve_top_k(body.question, settings=settings)

    store.append_turn(session_id, "user", body.question)

    async def generate():
        try:
            if err:
                resp = {
                    "answer": f"I can't answer right now: {err}",
                    "confidence": "low",
                    "session_id": session_id,
                }
                yield f"data: {json.dumps(resp)}\n\n"
                return

            if not hits:
                resp = {
                    "answer": "No relevant passages found for this question.",
                    "confidence": "low",
                    "session_id": session_id,
                }
                yield f"data: {json.dumps(resp)}\n\n"
                return

            # Stream answer tokens as they come
            full_answer = ""
            async for chunk in llm_service.generate_grounded_answer_stream(
                body.question,
                session_id,
                retrieval_hits=hits,
                retrieval_error=err,
                settings=settings,
                conversation_history=history_text,
            ):
                full_answer += chunk
                yield f"data: {json.dumps({'token': chunk, 'session_id': session_id})}\n\n"

            # Send final response
            store.append_turn(session_id, "assistant", full_answer)
            yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


_TTS_MAX_CHARS = 12000


async def _synthesize_answer_audio(
    text: str, settings
) -> tuple[AudioMetadata | None, str | None]:
    """
    Returns (metadata, error_message). error_message is set only on failure.
    """
    tts_text = (text or "").strip()
    if not tts_text:
        return None, "Nothing to synthesize (empty answer)."

    if len(tts_text) > _TTS_MAX_CHARS:
        tts_text = tts_text[: _TTS_MAX_CHARS - 1] + "…"

    try:
        local_service_url = getattr(settings, "tts_service_url", "http://localhost:9000")
        clean_url = getattr(settings, "clean_tts_url", "http://127.0.0.1:8010")
        backend = get_tts_backend(
            settings.tts_provider,
            service_url=local_service_url,
            clean_tts_url=clean_url,
        )
        result = await backend.synthesize(tts_text)

        if result.get("success"):
            logger.info("Answer audio synthesized: %sms", result.get("duration_ms"))
            url = result.get("audio_url")
            if not url and result.get("audio_wav_bytes"):
                import base64

                b64 = base64.b64encode(result["audio_wav_bytes"]).decode("ascii")
                url = f"data:audio/wav;base64,{b64}"
            return (
                AudioMetadata(
                    audio_url=url,
                    audio_path=result.get("audio_path"),
                    duration_ms=result.get("duration_ms"),
                    provider=result.get("provider", "unknown"),
                ),
                None,
            )

        msg = result.get("message") or "TTS synthesis failed."
        logger.debug("TTS synthesis failed: %s", msg)
        hint = (
            f"{msg} "
            "If using clean-xtts: start the service (see clean-tts/README.md) on "
            f"{clean_url}, or set TTS_PROVIDER=mock in backend/.env for a silent test clip."
        )
        return None, hint

    except Exception as e:
        logger.warning("Error attempting TTS synthesis: %s", e)
        return (
            None,
            f"{e!s} — check TTS_PROVIDER and that the TTS service is reachable.",
        )
