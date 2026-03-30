"""
TTS (Text-to-Speech) API route.

Exposes /api/tts endpoint for frontend to request audio synthesis.
Supports multiple backends: mock, local service (e.g., F5-TTS), and future embedded models.

## Binary response (recommended for browser)

Send header `Accept: audio/wav` to receive raw WAV bytes (faster than huge JSON+base64).
"""

import base64
import logging
import time

from fastapi import APIRouter, Request, Response

from app.core.config import get_settings
from app.schemas.tts import TTSRequest, TTSResponse
from app.services.tts_service import get_tts_backend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tts"])


@router.post("/tts", response_model=None)
async def synthesize_text(body: TTSRequest, request: Request) -> Response | TTSResponse:
    """
    Synthesize text into audio.

    - With `Accept: audio/wav` (or `audio/*`): returns raw WAV bytes (fast for the UI).
    - Otherwise: JSON metadata; `audio_url` may be a data URL (mock / legacy).
    """
    settings = get_settings()

    local_service_url = getattr(settings, "tts_service_url", "http://localhost:9000")
    clean_url = getattr(settings, "clean_tts_url", "http://127.0.0.1:8010")
    backend = get_tts_backend(
        settings.tts_provider,
        service_url=local_service_url,
        clean_tts_url=clean_url,
    )

    t0 = time.perf_counter()
    result = await backend.synthesize(body.text, body.voice_profile_id)
    t_syn = time.perf_counter() - t0

    logger.info(
        "portfolio_tts_proxy synthesize_s=%.3f provider=%s success=%s text_len=%s",
        t_syn,
        settings.tts_provider,
        result.get("success"),
        len(body.text),
    )

    accept = (request.headers.get("accept") or "").lower()
    want_wav = "audio/wav" in accept or "audio/*" in accept

    if result.get("success") and want_wav and result.get("audio_wav_bytes"):
        return Response(
            content=result["audio_wav_bytes"],
            media_type="audio/wav",
            headers={"Cache-Control": "no-store"},
        )

    if not result.get("success"):
        return TTSResponse(
            success=False,
            audio_url=None,
            audio_path=None,
            duration_ms=None,
            provider=result.get("provider", settings.tts_provider),
            message=result.get("message"),
        )

    audio_url = result.get("audio_url")
    if not audio_url and result.get("audio_wav_bytes"):
        b64 = base64.b64encode(result["audio_wav_bytes"]).decode("ascii")
        audio_url = f"data:audio/wav;base64,{b64}"

    return TTSResponse(
        success=True,
        audio_url=audio_url,
        audio_path=result.get("audio_path"),
        duration_ms=result.get("duration_ms"),
        provider=result.get("provider", settings.tts_provider),
        message=result.get("message"),
    )
