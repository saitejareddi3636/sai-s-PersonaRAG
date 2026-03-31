import logging
import os
import re
import time

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import get_settings
from app.rag.retrieve import retrieve_top_k
from app.schemas.chat import RetrievalHitSchema, SourceCitation
from app.schemas.voice import VoiceChatResponse
from app.services import llm_service
from app.services.session_store import get_session_store
from app.services.stt_service import transcribe_audio_bytes
from app.services.voice_service import VoiceOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])


def _compact_tts_text(answer_text: str, max_chars: int) -> str:
    """Build a short spoken version for faster voice playback without changing text answer."""
    text = (answer_text or "").strip()
    if not text:
        return text

    max_chars = max(120, int(max_chars))
    if len(text) <= max_chars:
        return text

    # Prefer the first 1-2 sentences when possible for a natural spoken summary.
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if sentences:
        short = sentences[0]
        if len(short) < max_chars and len(sentences) > 1:
            candidate = f"{short} {sentences[1]}"
            if len(candidate) <= max_chars:
                short = candidate
        if len(short) > max_chars:
            short = short[: max_chars - 1].rstrip() + "…"
        return short

    return text[: max_chars - 1].rstrip() + "…"


@router.post("/transcribe")
async def voice_transcribe_chunk(audio: UploadFile = File(...)):
    settings = get_settings()

    raw_audio = await audio.read()
    if not raw_audio:
        raise HTTPException(status_code=400, detail="No audio payload provided.")

    _, ext = os.path.splitext(audio.filename or "")
    suffix = ext or ".webm"

    stt = transcribe_audio_bytes(
        raw_audio,
        file_suffix=suffix,
        model_size=settings.stt_model_size,
        device=settings.stt_device,
        compute_type=settings.stt_compute_type,
        beam_size=settings.stt_beam_size,
        language=settings.stt_language,
    )

    if not stt.success:
        raise HTTPException(status_code=400, detail=stt.message or "Transcription failed.")

    return {
        "transcript": stt.transcript or "",
        "stt_provider": stt.provider,
        "stt_language": stt.language,
    }


@router.post("/chat", response_model=VoiceChatResponse)
async def voice_chat(
    audio: UploadFile = File(...),
    session_id: str | None = Form(default=None),
):
    settings = get_settings()

    raw_audio = await audio.read()
    if not raw_audio:
        raise HTTPException(status_code=400, detail="No audio payload provided.")

    _, ext = os.path.splitext(audio.filename or "")
    suffix = ext or ".webm"

    logger.info("voice_pipeline stage=stt start content_type=%s", audio.content_type)
    t0 = time.perf_counter()
    stt = transcribe_audio_bytes(
        raw_audio,
        file_suffix=suffix,
        model_size=settings.stt_model_size,
        device=settings.stt_device,
        compute_type=settings.stt_compute_type,
        beam_size=settings.stt_beam_size,
        language=settings.stt_language,
    )
    t_stt = time.perf_counter()

    if not stt.success or not stt.transcript:
        logger.info("voice_pipeline stage=stt failed reason=%s", stt.message)
        raise HTTPException(status_code=400, detail=stt.message or "Transcription failed.")

    store = get_session_store(settings.session_max_messages, settings.session_max_total_chars)
    resolved_session_id = store.ensure_session(session_id)
    history_text = store.get_history_text(resolved_session_id)

    logger.info("voice_pipeline stage=rag_chat start")
    hits, err = retrieve_top_k(stt.transcript, settings=settings)
    result = await llm_service.generate_grounded_answer(
        stt.transcript,
        resolved_session_id,
        retrieval_hits=hits,
        retrieval_error=err,
        settings=settings,
        conversation_history=history_text or None,
    )
    t_llm = time.perf_counter()

    store.append_turn(resolved_session_id, "user", stt.transcript)
    store.append_turn(resolved_session_id, "assistant", result.answer)

    logger.info("voice_pipeline stage=tts start provider=%s", settings.tts_provider)
    tts_text = _compact_tts_text(result.answer, settings.voice_tts_max_chars)
    if len(tts_text) < len(result.answer):
        logger.info(
            "voice_pipeline stage=tts compacted chars_in=%s chars_out=%s",
            len(result.answer),
            len(tts_text),
        )
    audio_metadata, tts_error = await VoiceOrchestrator.synthesize_answer_audio(tts_text, settings)
    t_tts = time.perf_counter()

    logger.info(
        "voice_pipeline done stt_s=%.3f rag_llm_s=%.3f tts_s=%.3f total_s=%.3f",
        t_stt - t0,
        t_llm - t_stt,
        t_tts - t_llm,
        t_tts - t0,
    )

    return VoiceChatResponse(
        transcript=stt.transcript,
        answer=result.answer,
        confidence=result.confidence,
        grounding_note=result.grounding_note,
        sources=[SourceCitation(excerpt=c.excerpt) for c in result.citations],
        session_id=resolved_session_id,
        audio=audio_metadata,
        tts_error=tts_error,
        retrieval=[RetrievalHitSchema(**h.to_api_dict()) for h in hits],
        retrieval_error=err,
        stt_provider=stt.provider,
        stt_language=stt.language,
    )
