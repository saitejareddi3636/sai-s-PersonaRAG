"""
In-process stack checks with **explicit assertion messages** (shown when a check fails).

These use TestClient — no separate `uvicorn` process. They still call real Ollama for
non-trivial /api/chat questions unless the app short-circuits (e.g. “hello”).

They do **not** load Faster-Whisper unless you hit /voice/transcribe with audio; the
silent-audio test only expects a 400 from the STT path.
"""

from __future__ import annotations

import struct
from io import BytesIO

from fastapi.testclient import TestClient


def _minimal_wav_silence(duration_ms: int = 600) -> bytes:
    sample_rate = 16000
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    bps = 2
    sub = num_samples * bps
    chunk = 36 + sub
    b = bytearray()
    b.extend(b"RIFF")
    b.extend(struct.pack("<I", chunk))
    b.extend(b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00")
    b.extend(struct.pack("<I", sample_rate))
    b.extend(struct.pack("<I", sample_rate * bps))
    b.extend(struct.pack("<H", bps))
    b.extend(struct.pack("<H", 16))
    b.extend(b"data")
    b.extend(struct.pack("<I", sub))
    b.extend(b"\x00" * sub)
    return bytes(b)


def test_health_ok(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200, f"GET /health -> {r.status_code} {r.text!r}"
    assert r.json() == {"status": "ok"}, r.json()


def test_chat_hello_returns_text(client: TestClient) -> None:
    r = client.post("/api/chat", json={"question": "hello", "include_tts": False})
    assert r.status_code == 200, f"POST /api/chat -> {r.status_code} {r.text[:800]!r}"
    data = r.json()
    ans = (data.get("answer") or "").strip()
    assert len(ans) >= 1, (
        f"Empty answer. Keys={sorted(data)} full={data!r}. "
        "If failures persist, ensure Ollama is up and OLLAMA_CHAT_MODEL is pulled."
    )


def test_chat_background_question_hits_llm_or_fallback(client: TestClient) -> None:
    """Stronger than 'hello': expects a non-trivial reply or explicit low-confidence path."""
    r = client.post(
        "/api/chat",
        json={"question": "What is your background?", "include_tts": False},
    )
    assert r.status_code == 200, f"POST /api/chat -> {r.status_code} {r.text[:800]!r}"
    data = r.json()
    ans = (data.get("answer") or "").strip()
    conf = data.get("confidence")
    assert conf in ("high", "medium", "low"), f"bad confidence={conf!r} body={data!r}"
    assert len(ans) >= 8, (
        f"Answer too short ({len(ans)} chars): {ans!r}. "
        "Check chunks.json / retrieval and Ollama connectivity."
    )


def test_tts_json_metadata_ok(client: TestClient) -> None:
    r = client.post(
        "/api/tts",
        json={"text": "One two three."},
        headers={"Accept": "application/json"},
    )
    assert r.status_code == 200, f"POST /api/tts -> {r.status_code} {r.text[:400]!r}"
    body = r.json()
    assert body.get("success") is True, (
        f"TTS failed: {body!r}. Set TTS_PROVIDER=mock for CI or configure Piper (PIPER_MODEL_PATH)."
    )
    assert body.get("provider"), f"missing provider in {body!r}"


def test_voice_transcribe_rejects_silence(client: TestClient) -> None:
    """Proves /api/voice/transcribe is wired; Faster-Whisper runs and should reject silence."""
    wav = _minimal_wav_silence()
    r = client.post(
        "/api/voice/transcribe",
        files={"audio": ("silence.wav", BytesIO(wav), "audio/wav")},
        timeout=180.0,
    )
    assert r.status_code == 400, (
        f"Expected 400 for silent WAV, got {r.status_code}: {r.text[:400]!r}. "
        "If 500, STT dependencies or model load may be broken."
    )
    detail = r.json().get("detail", r.text)
    assert detail, f"empty error detail: {r.text!r}"
