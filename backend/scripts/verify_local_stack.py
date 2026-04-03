#!/usr/bin/env python3
"""
Print whether LLM (Ollama), STT (Faster-Whisper), and TTS work on THIS machine.

This script always writes plain text to stdout (no pytest, no captured output).

Usage (from backend folder, with .env / venv as usual):

  cd backend
  source .venv/bin/activate   # if you use a venv
  python scripts/verify_local_stack.py

Exit code: 0 if all three pass, 1 if any fail.
"""

from __future__ import annotations

import asyncio
import struct
import sys
import time
import wave
from io import BytesIO
from pathlib import Path

# app imports after path fix
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _say(msg: str) -> None:
    print(msg, flush=True)


def _silent_wav() -> bytes:
    rate = 16000
    ms = 700
    n = int(rate * ms / 1000)
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b"\x00\x00" * n)
    return buf.getvalue()


def check_llm() -> tuple[bool, str]:
    import httpx

    from app.core.config import get_settings

    s = get_settings()
    base = s.ollama_base_url.rstrip("/")
    _say(f"[LLM] Ollama URL: {base}")
    _say(f"[LLM] Model: {s.ollama_chat_model}")

    t0 = time.perf_counter()
    try:
        with httpx.Client(timeout=120.0) as client:
            r = client.get(f"{base}/api/tags")
            if r.status_code != 200:
                return False, f"GET /api/tags -> HTTP {r.status_code} (is Ollama running?)"
            names = [m.get("name", "") for m in r.json().get("models", [])]
            if not any(s.ollama_chat_model in n or n.startswith(s.ollama_chat_model + ":") for n in names):
                return (
                    False,
                    f"Model '{s.ollama_chat_model}' not in `ollama list`. Pull it: ollama pull {s.ollama_chat_model}",
                )

            chat = client.post(
                f"{base}/api/chat",
                json={
                    "model": s.ollama_chat_model,
                    "messages": [{"role": "user", "content": 'Reply with exactly the word "pong".'}],
                    "stream": False,
                },
            )
            if chat.status_code != 200:
                return False, f"POST /api/chat -> HTTP {chat.status_code} {chat.text[:200]}"
            msg = (chat.json().get("message", {}) or {}).get("content", "") or ""
            msg = str(msg).strip()
            if len(msg) < 1:
                return False, "Empty reply from /api/chat"
    except httpx.ConnectError as e:
        return False, f"Cannot connect to Ollama at {base}: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

    dt = time.perf_counter() - t0
    return True, f"OK ({dt:.1f}s)"


def check_stt() -> tuple[bool, str]:
    from app.core.config import get_settings
    from app.services.stt_service import transcribe_audio_bytes

    s = get_settings()
    _say(f"[STT] Faster-Whisper size={s.stt_model_size} device={s.stt_device}")

    vp = None
    if s.stt_vad_filter:
        vp = {
            "min_silence_duration_ms": s.stt_vad_min_silence_duration_ms,
            "speech_pad_ms": s.stt_vad_speech_pad_ms,
        }

    t0 = time.perf_counter()
    try:
        result = transcribe_audio_bytes(
            _silent_wav(),
            file_suffix=".wav",
            model_size=s.stt_model_size,
            device=s.stt_device,
            compute_type=s.stt_compute_type,
            beam_size=s.stt_beam_size,
            language=s.stt_language,
            vad_filter=s.stt_vad_filter,
            vad_parameters=vp,
            without_timestamps=s.stt_without_timestamps,
        )
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

    dt = time.perf_counter() - t0
    if "not installed" in (result.message or "").lower():
        return False, "faster-whisper not installed in this Python env"
    # Silent audio: we expect no transcript (pipeline exercised).
    if result.success:
        return False, f"Silent WAV should not transcribe; got: {result.transcript!r}"
    if result.message and "speech" in result.message.lower():
        return True, f"OK — no speech on silence, as expected ({dt:.1f}s)"
    return True, f"OK — STT ran ({dt:.1f}s): {result.message}"


def check_tts() -> tuple[bool, str]:
    from app.core.config import get_settings
    from app.services.tts_service import get_tts_backend

    s = get_settings()
    _say(f"[TTS] Provider: {s.tts_provider}")

    t0 = time.perf_counter()
    try:
        backend = get_tts_backend(
            s.tts_provider,
            service_url=s.tts_service_url,
            piper_binary=s.piper_binary,
            piper_model_path=s.piper_model_path,
            piper_speaker_id=s.piper_speaker_id,
            piper_timeout_s=s.piper_timeout_s,
        )
        result = asyncio.run(backend.synthesize("Local stack check."))
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

    dt = time.perf_counter() - t0
    if not result.get("success"):
        return False, result.get("message") or "synthesis failed"

    if s.tts_provider == "mock":
        return True, f"OK — mock TTS ({dt:.2f}s); silent placeholder audio (set TTS_PROVIDER=piper + PIPER_MODEL_PATH for real speech)"

    wav = result.get("audio_wav_bytes")
    if wav and len(wav) > 100:
        return True, f"OK — {len(wav)} audio bytes ({dt:.1f}s)"
    url = result.get("audio_url") or ""
    if url.startswith("data:audio"):
        return True, f"OK — data URL audio ({dt:.1f}s)"
    return False, "No audio bytes or URL in response"


def main() -> int:
    _say("")
    _say("=" * 72)
    _say("  PersonaRAG — local check: LLM (Ollama) + STT + TTS")
    _say("  (Run from the `backend` directory so .env is picked up.)")
    _say("=" * 72)
    _say("")

    results: dict[str, tuple[bool, str]] = {}

    _say("--- 1. LLM (Ollama) ---")
    ok, msg = check_llm()
    results["LLM"] = (ok, msg)
    _say(f"  {'PASS' if ok else 'FAIL'} — {msg}")
    _say("")

    _say("--- 2. STT (Faster-Whisper) ---")
    ok, msg = check_stt()
    results["STT"] = (ok, msg)
    _say(f"  {'PASS' if ok else 'FAIL'} — {msg}")
    _say("")

    _say("--- 3. TTS ---")
    ok, msg = check_tts()
    results["TTS"] = (ok, msg)
    _say(f"  {'PASS' if ok else 'FAIL'} — {msg}")
    _say("")

    all_ok = all(v[0] for v in results.values())
    _say("=" * 72)
    if all_ok:
        _say("  SUMMARY: All three passed — reasonable to rely on the same stack in the cloud")
        _say("           (cloud still needs Ollama, Whisper deps, and Piper/model paths there).")
    else:
        _say("  SUMMARY: Fix failures above on this machine before expecting the cloud to work.")
    _say("=" * 72)
    _say("")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
