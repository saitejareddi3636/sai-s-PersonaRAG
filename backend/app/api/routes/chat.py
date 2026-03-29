"""
Chat API route with optional audio synthesis.

Handles Q&A with RAG retrieval. If include_tts=True, attempts to synthesize answer audio.
Graceful fallback: if TTS fails, text response is still returned (audio=None).
"""

import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.rag.retrieve import retrieve_top_k
from app.schemas.chat import AudioMetadata, ChatRequest, ChatResponse, RetrievalHitSchema, SourceCitation
from app.services import llm_service
from app.services.session_store import get_session_store
from app.services.tts_service import get_tts_backend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
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

    hits, err = retrieve_top_k(body.question, settings=settings)

    result = await llm_service.generate_grounded_answer(
        body.question,
        session_id,
        retrieval_hits=hits,
        retrieval_error=err,
        settings=settings,
        conversation_history=history_text or None,
    )

    store.append_turn(session_id, "user", body.question)
    store.append_turn(session_id, "assistant", result.answer)

    # Optionally synthesize audio
    audio_metadata = None
    if body.include_tts:
        audio_metadata = await _synthesize_answer_audio(result.answer, settings)

    return ChatResponse(
        answer=result.answer,
        confidence=result.confidence,
        grounding_note=result.grounding_note,
        sources=[
            SourceCitation(excerpt=c.excerpt)
            for c in result.citations
        ],
        session_id=session_id,
        audio=audio_metadata,
    )


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


async def _synthesize_answer_audio(
    text: str, settings
) -> AudioMetadata | None:
    """
    Attempt to synthesize answer audio. Gracefully handles failure.
    
    Args:
        text: Answer text to synthesize
        settings: Configuration object
        
    Returns:
        AudioMetadata on success; None if synthesis fails
        
    Note:
        Failures are logged but not raised; text response works regardless.
    """
    try:
        local_service_url = getattr(settings, 'tts_service_url', 'http://localhost:9000')
        backend = get_tts_backend(settings.tts_provider, service_url=local_service_url)
        result = await backend.synthesize(text)

        if result.get("success"):
            logger.info(f"Answer audio synthesized: {result.get('duration_ms')}ms")
            return AudioMetadata(
                audio_url=result.get("audio_url"),
                audio_path=result.get("audio_path"),
                duration_ms=result.get("duration_ms"),
                provider=result.get("provider", "unknown"),
            )
        else:
            logger.debug(f"TTS synthesis failed: {result.get('message')}")
            return None

    except Exception as e:
        logger.warning(f"Error attempting TTS synthesis: {e}")
        return None
