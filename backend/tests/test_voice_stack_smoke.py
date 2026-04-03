import asyncio
import os
import wave
from io import BytesIO

import pytest

from app.core.config import get_settings
from app.services.stt_service import transcribe_audio_bytes
from app.services.tts_service import get_tts_backend


def _silent_wav_bytes(duration_ms: int = 800, sample_rate: int = 16000) -> bytes:
    frame_count = int(sample_rate * (duration_ms / 1000.0))
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * frame_count)
    return buf.getvalue()


@pytest.mark.skipif(
    os.getenv("RUN_VOICE_SMOKE", "0") != "1",
    reason="Set RUN_VOICE_SMOKE=1 to run local STT/TTS smoke tests.",
)
def test_faster_whisper_stt_smoke() -> None:
    settings = get_settings()

    print(
        "\n[RUN_VOICE_SMOKE] Faster-Whisper: loading model if needed, transcribing silent WAV…",
        flush=True,
    )
    # A silent clip should still exercise model loading and decoding.
    vp = None
    if settings.stt_vad_filter:
        vp = {
            "min_silence_duration_ms": settings.stt_vad_min_silence_duration_ms,
            "speech_pad_ms": settings.stt_vad_speech_pad_ms,
        }
    result = transcribe_audio_bytes(
        _silent_wav_bytes(),
        file_suffix=".wav",
        model_size=settings.stt_model_size,
        device=settings.stt_device,
        compute_type=settings.stt_compute_type,
        beam_size=settings.stt_beam_size,
        language=settings.stt_language,
        vad_filter=settings.stt_vad_filter,
        vad_parameters=vp,
        without_timestamps=settings.stt_without_timestamps,
    )

    assert result.provider == "faster-whisper"
    assert result.message is None or "No speech detected" in result.message
    assert "not installed" not in (result.message or "")
    print(f"[RUN_VOICE_SMOKE] STT result: success={result.success} msg={result.message!r}", flush=True)


@pytest.mark.skipif(
    os.getenv("RUN_VOICE_SMOKE", "0") != "1",
    reason="Set RUN_VOICE_SMOKE=1 to run local STT/TTS smoke tests.",
)
def test_piper_tts_smoke() -> None:
    settings = get_settings()

    print("\n[RUN_VOICE_SMOKE] Piper TTS synthesis…", flush=True)
    if settings.tts_provider != "piper":
        pytest.skip("TTS_PROVIDER is not set to 'piper'.")

    if not settings.piper_model_path:
        pytest.skip("PIPER_MODEL_PATH is not configured.")

    backend = get_tts_backend(
        settings.tts_provider,
        service_url=settings.tts_service_url,
        piper_binary=settings.piper_binary,
        piper_model_path=settings.piper_model_path,
        piper_speaker_id=settings.piper_speaker_id,
        piper_timeout_s=settings.piper_timeout_s,
    )

    result = asyncio.run(backend.synthesize("This is a Piper smoke test."))

    assert result.get("success") is True, result.get("message")
    assert result.get("provider") == "piper"
    assert result.get("audio_wav_bytes") is not None
    n = len(result["audio_wav_bytes"])
    print(f"[RUN_VOICE_SMOKE] TTS OK: wav_bytes={n}", flush=True)
