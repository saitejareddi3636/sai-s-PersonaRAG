"""
TTS (Text-to-Speech) API route.

Exposes /api/tts endpoint for frontend to request audio synthesis.
Supports multiple backends: mock, local service (e.g., F5-TTS), and future embedded models.

## Graceful degradation

If TTS synthesis fails:
- Response has success=False
- Frontend should show text-only answer (normal chat flow)
- User can still read the answer without audio

## Local TTS service

To enable local TTS service:
1. Start local F5-TTS service on http://localhost:9000 (or configured URL)
2. Set TTS_PROVIDER=local-service in backend/.env
3. POST /api/tts will call the local service
4. If service unavailable, gracefully returns error
"""

import logging

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.tts import TTSRequest, TTSResponse
from app.services.tts_service import get_tts_backend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tts"])


@router.post("/tts", response_model=TTSResponse)
async def synthesize_text(body: TTSRequest) -> TTSResponse:
    """
    Synthesize text into audio.

    Accepts plain text and optional voice profile ID.
    Returns metadata about synthesized audio (URL, duration, etc.).

    Supports multiple TTS backends:
    - mock: Returns mocked audio metadata (always works)
    - local-service: Calls external TTS service (graceful fallback if unavailable)
    - f5-tts: Placeholder for future embedded model

    Args:
        body: TTSRequest with text and optional voice_profile_id

    Returns:
        TTSResponse with audio metadata and reference
        
    Note:
        If TTS synthesis fails, success=False; frontend should fall back to text-only.
    """
    settings = get_settings()
    
    # Get configured service URL if using local service
    local_service_url = getattr(settings, 'tts_service_url', 'http://localhost:9000')
    
    backend = get_tts_backend(settings.tts_provider, service_url=local_service_url)

    result = await backend.synthesize(body.text, body.voice_profile_id)

    logger.info(
        f"TTS synthesis: provider={settings.tts_provider}, "
        f"success={result.get('success')}, text_len={len(body.text)}"
    )

    return TTSResponse(
        success=result["success"],
        audio_url=result.get("audio_url"),
        audio_path=result.get("audio_path"),
        duration_ms=result.get("duration_ms"),
        provider=result.get("provider", settings.tts_provider),
        message=result.get("message"),
    )
