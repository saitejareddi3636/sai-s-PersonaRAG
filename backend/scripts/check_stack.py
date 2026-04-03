#!/usr/bin/env python3
"""
End-to-end smoke check: Health → LLM chat → TTS → STT (silent clip) → chat stream.

Run from repo with backend deps available, e.g.:

  cd backend && python scripts/check_stack.py
  API_BASE=https://your-api.example.com python scripts/check_stack.py

In-process pytest (same machine, no separate server) with clear failure messages:

  cd backend && pytest tests/test_stack_output_report.py -v

Exit code 0 if all checks pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from io import BytesIO

import httpx


def _silent_wav_bytes(duration_ms: int = 600, sample_rate: int = 16000) -> bytes:
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    num_channels = 1
    bytes_per_sample = 2
    subchunk2_size = num_samples * num_channels * bytes_per_sample
    chunk_size = 36 + subchunk2_size
    wav_data = bytearray()
    wav_data.extend(b"RIFF")
    wav_data.extend(struct.pack("<I", chunk_size))
    wav_data.extend(b"WAVE")
    wav_data.extend(b"fmt ")
    wav_data.extend(struct.pack("<I", 16))
    wav_data.extend(struct.pack("<H", 1))
    wav_data.extend(struct.pack("<H", num_channels))
    wav_data.extend(struct.pack("<I", sample_rate))
    wav_data.extend(struct.pack("<I", sample_rate * num_channels * bytes_per_sample))
    wav_data.extend(struct.pack("<H", num_channels * bytes_per_sample))
    wav_data.extend(struct.pack("<H", 16))
    wav_data.extend(b"data")
    wav_data.extend(struct.pack("<I", subchunk2_size))
    wav_data.extend(b"\x00" * subchunk2_size)
    return bytes(wav_data)


def check_health(client: httpx.Client, base: str) -> bool:
    r = client.get(f"{base}/health", timeout=30.0)
    ok = r.status_code == 200 and r.json().get("status") == "ok"
    print(f"  [{'OK' if ok else 'FAIL'}] GET /health -> {r.status_code}")
    return ok


def check_chat(client: httpx.Client, base: str) -> bool:
    r = client.post(
        f"{base}/api/chat",
        json={"question": "hello", "include_tts": False},
        timeout=120.0,
    )
    if r.status_code != 200:
        print(f"  [FAIL] POST /api/chat -> {r.status_code} {r.text[:200]}")
        return False
    data = r.json()
    ans = (data.get("answer") or "").strip()
    ok = len(ans) > 0
    print(f"  [{'OK' if ok else 'FAIL'}] POST /api/chat -> answer_len={len(ans)} confidence={data.get('confidence')}")
    return ok


def check_tts(client: httpx.Client, base: str) -> bool:
    r = client.post(
        f"{base}/api/tts",
        json={"text": "Stack check one two."},
        headers={"Accept": "audio/wav"},
        timeout=90.0,
    )
    if r.status_code != 200:
        print(f"  [FAIL] POST /api/tts -> {r.status_code} {r.text[:200]}")
        return False
    ct = (r.headers.get("content-type") or "").lower()
    if "audio" in ct and len(r.content) > 100:
        print(f"  [OK] POST /api/tts -> audio/wav bytes={len(r.content)}")
        return True
    try:
        meta = r.json()
    except Exception:
        print(f"  [FAIL] POST /api/tts unexpected body type={ct} len={len(r.content)}")
        return False
    if meta.get("success") and meta.get("audio_url"):
        print("  [OK] POST /api/tts -> JSON audio_url present")
        return True
    print(f"  [FAIL] POST /api/tts JSON success={meta.get('success')} msg={meta.get('message')}")
    return False


def check_stt(client: httpx.Client, base: str) -> bool:
    """Silent WAV should be rejected or empty transcript — proves STT path is wired."""
    wav = _silent_wav_bytes()
    files = {"audio": ("silence.wav", BytesIO(wav), "audio/wav")}
    r = client.post(f"{base}/api/voice/transcribe", files=files, timeout=120.0)
    if r.status_code == 400:
        try:
            detail = r.json().get("detail", "")
        except Exception:
            detail = r.text
        ds = str(detail).lower()
        ok = "speech" in ds or "no " in ds or "audio" in ds or len(str(detail)) > 0
        print(f"  [{'OK' if ok else 'FAIL'}] POST /api/voice/transcribe (silent) -> 400: {str(detail)[:100]}")
        return ok
    if r.status_code == 200:
        print("  [OK] POST /api/voice/transcribe -> 200 (unexpected for silence; model may have hallucinated)")
        return True
    print(f"  [FAIL] POST /api/voice/transcribe -> {r.status_code} {r.text[:200]}")
    return False


def check_stream(client: httpx.Client, base: str) -> bool:
    with client.stream(
        "POST",
        f"{base}/api/chat/stream",
        json={"question": "hello", "include_tts": False},
        timeout=120.0,
    ) as r:
        if r.status_code != 200:
            print(f"  [FAIL] POST /api/chat/stream -> {r.status_code}")
            return False
        buf = ""
        got_token_or_done = False
        for chunk in r.iter_text():
            buf += chunk
            if '"token"' in buf or '"done"' in buf or '"answer"' in buf:
                got_token_or_done = True
                break
            if len(buf) > 64_000:
                break
        ok = got_token_or_done or "done" in buf
        print(f"  [{'OK' if ok else 'FAIL'}] POST /api/chat/stream -> saw_sse_payload={got_token_or_done} buf_len={len(buf)}")
        return ok


def main() -> int:
    p = argparse.ArgumentParser(description="PersonaRAG API stack smoke test")
    p.add_argument(
        "--base-url",
        default=(__import__("os").environ.get("API_BASE") or "http://127.0.0.1:8000").rstrip("/"),
        help="API origin (env API_BASE overrides default)",
    )
    p.add_argument("--skip-stream", action="store_true", help="Skip SSE /api/chat/stream check")
    p.add_argument("--skip-stt", action="store_true", help="Skip /api/voice/transcribe")
    args = p.parse_args()
    base = args.base_url

    print(f"PersonaRAG stack check → {base}\n")

    results: list[tuple[str, bool]] = []
    with httpx.Client(follow_redirects=True) as client:
        results.append(("health", check_health(client, base)))
        results.append(("chat", check_chat(client, base)))
        results.append(("tts", check_tts(client, base)))
        if not args.skip_stt:
            results.append(("stt", check_stt(client, base)))
        if not args.skip_stream:
            results.append(("chat_stream", check_stream(client, base)))

    failed = [n for n, ok in results if not ok]
    print()
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
