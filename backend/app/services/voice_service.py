"""
Voice service layer for TTS synthesis and voice pipeline orchestration.

Centralizes voice-specific operations to avoid cross-module dependencies.
"""

import base64
import logging

from app.core.config import Settings
from app.schemas.chat import AudioMetadata
from app.services.tts_service import get_tts_backend

logger = logging.getLogger(__name__)

_TTS_MAX_CHARS = 12000


class VoiceOrchestrator:
    """Orchestrator for voice-related operations (TTS synthesis, etc.)."""

    @staticmethod
    async def synthesize_answer_audio(
        text: str, settings: Settings
    ) -> tuple[AudioMetadata | None, str | None]:
        """
        Synthesize answer text to audio metadata.

        Returns:
            (metadata, error_message) tuple where error_message is set only on failure.
        """
        tts_text = (text or "").strip()
        if not tts_text:
            return None, "Nothing to synthesize (empty answer)."

        if len(tts_text) > _TTS_MAX_CHARS:
            tts_text = tts_text[: _TTS_MAX_CHARS - 1] + "…"

        try:
            local_service_url = getattr(settings, "tts_service_url", "http://localhost:9000")
            backend = get_tts_backend(
                settings.tts_provider,
                service_url=local_service_url,
                piper_binary=getattr(settings, "piper_binary", "piper"),
                piper_model_path=getattr(settings, "piper_model_path", ""),
                piper_speaker_id=getattr(settings, "piper_speaker_id", None),
                piper_timeout_s=getattr(settings, "piper_timeout_s", 45.0),
            )
            result = await backend.synthesize(tts_text)

            if result.get("success"):
                logger.info("Answer audio synthesized: %sms", result.get("duration_ms"))
                url = result.get("audio_url")
                if not url and result.get("audio_wav_bytes"):
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
                "Check TTS_PROVIDER configuration. For Piper set PIPER_MODEL_PATH and ensure "
                "the piper binary is installed."
            )
            return None, hint

        except Exception as e:
            logger.warning("Error attempting TTS synthesis: %s", e)
            return (
                None,
                f"{e!s} — check TTS_PROVIDER and that the TTS service is reachable.",
            )
