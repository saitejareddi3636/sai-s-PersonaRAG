"""
TTS (Text-to-Speech) service for synthesizing recruiter answers into audio.

## Architecture

This service abstracts multiple TTS backends:
- MockTTSBackend: Development & testing (no dependencies)
- LocalTTSServiceAdapter: Calls external local service (e.g., F5-TTS)
- F5TTSBackend: Planned for future embedded model

## Integration points

- Backend: /api/tts POST endpoint (see routes/tts.py)
- Config: TTS_PROVIDER env var ("mock", "local-service", "f5-tts")
- Local service: Expects HTTP API on port 9000 (configurable)

## Local TTS Service Contract

Expected external service (e.g., F5-TTS):
- **Base URL**: http://localhost:9000 (default)
- **Endpoint**: POST /synthesize
- **Request**: {"text": str, "voice_id": str | null}
- **Response**: 
  {
    "success": true,
    "audio_url": "file path or URL",
    "duration_ms": int,
    "format": "wav" | "mp3" | "ogg"
  }
- **Error behavior**: 5xx on failure; client handles gracefully
- **Availability**: Optional; text chat works without it

## Integration flow

1. /api/tts POST request arrives
2. TTS service factory picks backend (mock, local-service, f5-tts)
3. If local-service:
   a. LocalTTSServiceAdapter calls HTTP client
   b. If service unavailable → return graceful error
   c. If service responds → return audio metadata
4. Response sent to frontend (or error message)
5. If synthesis fails, text response still works (fallback in frontend)
"""

import base64
import io
import logging
import wave
from abc import ABC, abstractmethod

from app.services.piper_tts_client import PiperTTSClient

logger = logging.getLogger(__name__)


class TTSBackend(ABC):
    """Abstract base for TTS providers."""

    @abstractmethod
    async def synthesize(
        self, text: str, voice_profile_id: str | None = None
    ) -> dict:
        """
        Synthesize text into audio.

        Args:
            text: Text to synthesize
            voice_profile_id: Optional voice identifier

        Returns:
            dict with keys:
                - success: bool
                - audio_url: str | None (URL to audio)
                - audio_path: str | None (internal file path)
                - duration_ms: int | None (milliseconds)
                - message: str | None (status or error)
                - provider: str (backend name)
        """
        pass


def _minimal_silent_wav() -> tuple[str, bytes, int]:
    """Short silent WAV: data URL, raw bytes, duration_ms."""
    buf = io.BytesIO()
    rate = 22050
    frames = int(rate * 0.4)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b"\x00\x00" * frames)
    wav_bytes = buf.getvalue()
    b64 = base64.b64encode(wav_bytes).decode("ascii")
    duration_ms = int(round(frames / float(rate) * 1000))
    return f"data:audio/wav;base64,{b64}", wav_bytes, duration_ms


class MockTTSBackend(TTSBackend):
    """
    Mock TTS backend for development and testing.
    Returns a playable silent clip (data URL) so the Voice UI works without a TTS server.
    """

    async def synthesize(
        self, text: str, voice_profile_id: str | None = None
    ) -> dict:
        word_count = len(text.split())
        estimated_duration_ms = int((word_count / 150) * 60 * 1000)
        estimated_duration_ms = max(500, min(estimated_duration_ms, 300000))

        voice_label = voice_profile_id or "default"
        data_url, wav_bytes, _clip_ms = _minimal_silent_wav()

        return {
            "success": True,
            "audio_url": data_url,
            "audio_wav_bytes": wav_bytes,
            "audio_path": None,
            "duration_ms": estimated_duration_ms,
            "provider": "mock",
            "message": (
                f"Mock TTS: silent placeholder clip ({word_count} words, voice={voice_label}); "
                f"set TTS_PROVIDER=piper for real speech."
            ),
        }


class LocalTTSServiceAdapter(TTSBackend):
    """
    Adapter for calling a local TTS service (e.g., F5-TTS running separately).
    
    Gracefully handles service unavailability; falls back to error response.
    """

    def __init__(self, local_service_url: str = "http://localhost:9000"):
        """
        Initialize adapter.

        Args:
            local_service_url: Base URL of local TTS service
        """
        from app.services.local_tts_client import LocalTTSClient

        self.client = LocalTTSClient(base_url=local_service_url)

    async def synthesize(
        self, text: str, voice_profile_id: str | None = None
    ) -> dict:
        """
        Call local TTS service; gracefully handle unavailability.

        Returns:
            dict with audio metadata on success
            dict with success=False if service unavailable or fails
        """
        result = await self.client.synthesize(text, voice_profile_id)

        if result:
            return result

        # Service unavailable or failed
        return {
            "success": False,
            "audio_url": None,
            "audio_path": None,
            "duration_ms": None,
            "provider": "local-f5-tts",
            "message": "Local TTS service unavailable; audio synthesis failed",
        }


# XTTS backend disabled in active runtime path.
# class CleanXTTSBackend(TTSBackend):
#     ...


class F5TTSBackend(TTSBackend):
    """
    F5-TTS backend for local speech synthesis.
    
    Placeholder for future implementation.
    Will be activated when:
    1. F5-TTS model is downloaded and cached
    2. TTS_PROVIDER env var is set to "f5-tts"
    3. Model is loaded in app startup
    """

    def __init__(self):
        raise NotImplementedError(
            "F5-TTS backend not yet available. "
            "Set TTS_PROVIDER='mock' or 'local-service' for now."
        )

    async def synthesize(
        self, text: str, voice_profile_id: str | None = None
    ) -> dict:
        """F5-TTS synthesis (not yet implemented)."""
        raise NotImplementedError("F5-TTS not yet integrated")


class PiperTTSBackend(TTSBackend):
    """Piper local CPU TTS backend."""

    def __init__(
        self,
        *,
        piper_binary: str = "piper",
        model_path: str = "",
        speaker_id: int | None = None,
        timeout_s: float = 45.0,
    ):
        self.client = PiperTTSClient(
            piper_binary=piper_binary,
            model_path=model_path,
            speaker_id=speaker_id,
            synth_timeout_s=timeout_s,
        )

    async def synthesize(
        self, text: str, voice_profile_id: str | None = None
    ) -> dict:
        _ = voice_profile_id
        return await self.client.synthesize(text)


# Cache backends by configuration to avoid recreating per request
_TTS_BACKEND_CACHE: dict[tuple, TTSBackend] = {}


def get_tts_backend(
    provider: str = "mock",
    service_url: str = "http://localhost:9000",
    *,
    piper_binary: str = "piper",
    piper_model_path: str = "",
    piper_speaker_id: int | None = None,
    piper_timeout_s: float = 45.0,
) -> TTSBackend:
    """
    Factory to get a TTS backend by name.

    Backends are cached to avoid recreating per request (e.g., Piper model loading).

    Args:
        provider: "piper" | "mock" | "local-service" | "f5-tts"
        service_url: Base URL for local-service provider
        piper_binary: Piper command/path
        piper_model_path: Path to .onnx model
        piper_speaker_id: Speaker ID (for multi-speaker models)
        piper_timeout_s: Timeout in seconds

    Returns:
        Instantiated TTSBackend (may be cached)

    Raises:
        ValueError: If provider is unknown or not available
    """
    if provider == "mock":
        # Mock is stateless, no need to cache
        return MockTTSBackend()

    if provider == "piper":
        # Cache by config tuple to reuse backends
        cache_key = ("piper", piper_binary, piper_model_path, piper_speaker_id, piper_timeout_s)
        if cache_key not in _TTS_BACKEND_CACHE:
            _TTS_BACKEND_CACHE[cache_key] = PiperTTSBackend(
                piper_binary=piper_binary,
                model_path=piper_model_path,
                speaker_id=piper_speaker_id,
                timeout_s=piper_timeout_s,
            )
        return _TTS_BACKEND_CACHE[cache_key]

    if provider == "local-service":
        # Cache by service URL
        cache_key = ("local-service", service_url)
        if cache_key not in _TTS_BACKEND_CACHE:
            _TTS_BACKEND_CACHE[cache_key] = LocalTTSServiceAdapter(local_service_url=service_url)
        return _TTS_BACKEND_CACHE[cache_key]

    # XTTS provider is intentionally disabled.
    if provider == "clean-xtts":
        raise ValueError("TTS provider 'clean-xtts' is disabled. Use 'piper'.")

    if provider == "f5-tts":
        return F5TTSBackend()

    raise ValueError(f"Unknown TTS provider: {provider}")
