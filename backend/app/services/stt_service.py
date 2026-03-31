import logging
import time
from dataclasses import dataclass
from io import BytesIO

logger = logging.getLogger(__name__)
_SERVICE_CACHE: dict[tuple[str, str, str, int], "FasterWhisperSTTService"] = {}

# Minimum audio payload size in bytes (~80ms at 16kHz)
_MIN_AUDIO_SIZE = 2560


@dataclass
class STTResult:
    success: bool
    transcript: str | None
    provider: str
    language: str | None = None
    message: str | None = None


def _validate_audio_payload(audio_bytes: bytes) -> tuple[bool, str | None]:
    """
    Validate audio payload before transcription.

    Returns:
        (is_valid, error_message) where error_message is None if valid.
    """
    if not audio_bytes:
        return False, "No audio payload provided."

    if len(audio_bytes) < _MIN_AUDIO_SIZE:
        return False, f"Audio too short ({len(audio_bytes)} bytes). Minimum: {_MIN_AUDIO_SIZE}."

    return True, None


class FasterWhisperSTTService:
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        beam_size: int = 1,
        vad_filter: bool = True,
        language: str | None = None,
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self.language = language
        self._model = None

    def _get_model(self):
        if self._model is not None:
            return self._model

        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise RuntimeError(
                "faster-whisper is not installed. Install backend dependencies first."
            )

        logger.info(
            "Loading Faster-Whisper model size=%s device=%s compute_type=%s",
            self.model_size,
            self.device,
            self.compute_type,
        )
        self._model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )
        return self._model

    def transcribe_bytes(self, audio_bytes: bytes) -> STTResult:
        """
        Transcribe audio bytes to text.

        Optimized for Mac CPU:
        - Model size: base (fast, accurate enough)
        - Compute: int8 (fastest on CPU)
        - Beam size: 1 (greedy, no search overhead)
        """
        t0 = time.perf_counter()

        # Validate payload first
        is_valid, validation_error = _validate_audio_payload(audio_bytes)
        if not is_valid:
            return STTResult(
                success=False,
                transcript=None,
                provider="faster-whisper",
                message=validation_error,
            )

        try:
            model = self._get_model()
            segments, info = model.transcribe(
                BytesIO(audio_bytes),
                beam_size=self.beam_size,
                vad_filter=self.vad_filter,
                condition_on_previous_text=False,
                language=self.language,
            )
            
            transcript = " ".join((s.text or "").strip() for s in segments).strip()
            elapsed = time.perf_counter() - t0
            lang = getattr(info, "language", None)

            logger.info(
                "voice_stt done_s=%.3f language=%s chars=%s",
                elapsed,
                lang,
                len(transcript),
            )

            if not transcript:
                return STTResult(
                    success=False,
                    transcript=None,
                    provider="faster-whisper",
                    language=lang,
                    message="No speech detected. Please try again.",
                )

            return STTResult(
                success=True,
                transcript=transcript,
                provider="faster-whisper",
                language=lang,
            )

        except Exception as e:
            elapsed = time.perf_counter() - t0
            logger.warning("voice_stt failed after %.3fs: %s", elapsed, e)
            return STTResult(
                success=False,
                transcript=None,
                provider="faster-whisper",
                message=f"Transcription failed: {e}",
            )


def transcribe_audio_bytes(
    audio_bytes: bytes,
    *,
    file_suffix: str,
    model_size: str,
    device: str,
    compute_type: str,
    beam_size: int,
    language: str | None = None,
) -> STTResult:
    """
    Transcribe audio bytes to text using Faster-Whisper.

    Args:
        audio_bytes: Raw audio data
        file_suffix: File extension (e.g., '.webm', '.wav') - informational only
        model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        device: 'cpu' or 'cuda'
        compute_type: 'int8', 'int16', 'float16', 'float32'
        beam_size: Beam search width (1=greedy fastest, higher=slower)
        language: Optional language code ('en', 'es', etc.) for faster/better recognition

    Returns:
        STTResult with success, transcript, provider, language, message
    """
    if not audio_bytes:
        return STTResult(
            success=False,
            transcript=None,
            provider="faster-whisper",
            message="No audio payload provided.",
        )

    _ = file_suffix  # Kept for interface compatibility
    cache_key = (model_size, device, compute_type, beam_size)
    service = _SERVICE_CACHE.get(cache_key)
    if service is None:
        service = FasterWhisperSTTService(
            model_size=model_size,
            device=device,
            compute_type=compute_type,
            beam_size=beam_size,
            language=language,
        )
        _SERVICE_CACHE[cache_key] = service

    return service.transcribe_bytes(audio_bytes)
