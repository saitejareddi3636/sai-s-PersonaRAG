#!/usr/bin/env python3
"""
Print a markdown comparison table from real HTTP timings (headers + wall clock),
plus WAV response size and decoded audio duration for normalization.

Flow matches deferred voice: POST /api/chat (text only) then POST clean-tts /tts.

Prerequisites:
  - PersonaRAG backend (default http://127.0.0.1:8000)
  - clean-tts (default http://127.0.0.1:8010)

Send header ``X-Benchmark: 1`` on both requests so servers attach timing headers.

Environment:
  API_BASE, CLEAN_TTS_BASE — base URLs without trailing slash
  TTS_CHAR_BUDGET — must match frontend (default 500)

Usage:
  python scripts/benchmark_voice_latency_table.py
"""

from __future__ import annotations

import io
import json
import os
import sys
import time
import wave
import urllib.error
import urllib.request
from typing import Any

# Match frontend/lib/api.ts TTS_VOICE_CHAR_BUDGET
TTS_CHAR_BUDGET = int(os.environ.get("TTS_CHAR_BUDGET", "500"))

PROMPTS: list[tuple[str, str]] = [
    (
        "short",
        "Reply in exactly one clear sentence: what is 2+2?",
    ),
    (
        "medium",
        "In two or three sentences, explain what a resume summary is and why recruiters skim it.",
    ),
    (
        "long",
        "Write a detailed answer in about 8–10 sentences explaining how fractional reserve "
        "banking works in plain language, including deposits, lending, and the role of "
        "central bank reserves. Be concrete but accessible.",
    ),
]


def _header(headers: Any, name: str) -> str | None:
    """Case-insensitive header lookup (urllib uses Title-Case keys)."""
    want = name.lower()
    if hasattr(headers, "get_all"):
        # email.message.Message in some Python versions
        for k, v in headers.items():
            if k.lower() == want:
                return v
    for k, v in headers.items():
        if k.lower() == want:
            return v
    return None


def _fhdr(headers: Any, name: str) -> float | None:
    raw = _header(headers, name)
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def wav_duration_seconds(raw: bytes) -> float | None:
    """PCM WAV duration from response body (stdlib only)."""
    try:
        with wave.open(io.BytesIO(raw), "rb") as w:
            nframes = w.getnframes()
            rate = w.getframerate()
            if rate <= 0:
                return None
            return nframes / float(rate)
    except (wave.Error, EOFError, ValueError):
        return None


def text_for_voice_tts(full: str) -> str:
    t = full.strip()
    if len(t) <= TTS_CHAR_BUDGET:
        return t
    return f"{t[: TTS_CHAR_BUDGET - 1]}…"


def post_json(
    url: str,
    payload: dict[str, Any],
    extra_headers: dict[str, str] | None = None,
) -> tuple[Any, dict[str, Any]]:
    data = json.dumps(payload).encode("utf-8")
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if extra_headers:
        h.update(extra_headers)
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=600) as resp:
        body = resp.read()
        parsed = json.loads(body.decode("utf-8"))
        return resp.headers, parsed


def post_tts_wav(
    url: str, text: str, extra_headers: dict[str, str] | None = None
) -> tuple[Any, bytes]:
    payload = {"text": text, "language": "en"}
    data = json.dumps(payload).encode("utf-8")
    h = {"Content-Type": "application/json", "Accept": "audio/wav"}
    if extra_headers:
        h.update(extra_headers)
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=600) as resp:
        body = resp.read()
        return resp.headers, body


def main() -> int:
    api_base = os.environ.get("API_BASE", "http://127.0.0.1:8000").rstrip("/")
    tts_base = os.environ.get("CLEAN_TTS_BASE", "http://127.0.0.1:8010").rstrip("/")
    chat_url = f"{api_base}/api/chat"
    tts_url = f"{tts_base}/tts"
    bench_h = {"X-Benchmark": "1"}

    rows: list[list[str]] = []
    for label, question in PROMPTS:
        t_wall0 = time.perf_counter()
        try:
            ch, data = post_json(
                chat_url,
                {"question": question, "include_tts": False},
                bench_h,
            )
        except urllib.error.URLError as e:
            print(f"Chat request failed ({chat_url}): {e}", file=sys.stderr)
            return 1
        answer = data.get("answer") or ""
        clip = text_for_voice_tts(answer)
        try:
            th, audio_bytes = post_tts_wav(tts_url, clip, bench_h)
        except urllib.error.URLError as e:
            print(f"TTS request failed ({tts_url}): {e}", file=sys.stderr)
            return 1
        t_wall1 = time.perf_counter()

        llm_s = _fhdr(ch, "X-Benchmark-Llm-S")
        cond_s = _fhdr(th, "X-Benchmark-Conditioning-S")
        gen_s = _fhdr(th, "X-Benchmark-Generation-S")
        wav_s = _fhdr(th, "X-Benchmark-Wav-Encode-S")
        route_s = _fhdr(th, "X-Benchmark-Route-Total-S")
        perceived = t_wall1 - t_wall0
        n_bytes = len(audio_bytes)
        audio_s = wav_duration_seconds(audio_bytes)

        def fmt(x: float | None) -> str:
            return f"{x:.3f}" if x is not None else "n/a"

        rows.append(
            [
                label,
                fmt(llm_s),
                fmt(cond_s),
                fmt(gen_s),
                fmt(wav_s),
                fmt(route_s),
                f"{perceived:.3f}",
                str(n_bytes),
                fmt(audio_s),
            ]
        )

    print("Deferred voice path: chat (benchmark headers) → clip answer to TTS budget → clean-tts /tts.")
    print(f"TTS clip budget: {TTS_CHAR_BUDGET} chars (matches frontend).\n")
    print(
        "| prompt | llm_s | conditioning_s | generation_s | "
        "wav_encode_s | route_total_s (tts) | perceived_total_s | audio_bytes | audio_duration_s |"
    )
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in rows:
        print("| " + " | ".join(r) + " |")
    print()
    print(
        "**Perceived** = wall clock from start of chat POST until TTS response body is fully read "
        "(includes network; chat excludes TTS). **route_total_s** is clean-tts server-side for /tts. "
        "**audio_bytes** / **audio_duration_s** come from the WAV body (encode size + decoded length); "
        "use them to separate heavier synthesis from larger transfer."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
