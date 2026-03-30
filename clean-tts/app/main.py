from __future__ import annotations

import io
import logging
import os
import time
from contextlib import asynccontextmanager

import soundfile as sf
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.engine import get_engine
from app.paths import default_speaker_path, resolve_speaker_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Default: warm model + cache conditioning for default speaker + one tiny synthesis (JIT).
    Set CLEAN_TTS_WARMUP=0 to skip (faster process start, slower first request).
    """
    if os.environ.get("CLEAN_TTS_WARMUP", "1") != "0":
        try:
            ref = default_speaker_path()
            if ref is not None and ref.is_file():
                eng = get_engine()
                rp = str(ref.resolve())
                t0 = time.perf_counter()
                eng.warm_speaker_file(rp)
                _ = eng.synthesize("Hi.", speaker_wav=rp, language="en", split_sentences=False)
                logger.info(
                    "clean-tts warmup done in %.3fs (CLEAN_TTS_WARMUP=1 default; set CLEAN_TTS_WARMUP=0 to skip)",
                    time.perf_counter() - t0,
                )
            else:
                logger.warning("clean-tts warmup skipped: no default reference audio")
        except Exception as e:
            logger.warning("clean-tts warmup failed: %s", e)
    yield


app = FastAPI(title="clean-tts", version="0.1.0", lifespan=lifespan)


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to speak")
    language: str = Field(default="en", min_length=2, max_length=8)
    speaker_wav: str | None = Field(
        default=None,
        description="Optional path relative to clean-tts/, e.g. samples/voice.wav. "
        "If omitted, uses samples/voice.wav or repo-root sai_audio.m4a.",
    )


@app.get("/health")
def health() -> dict[str, str]:
    ref = default_speaker_path()
    return {
        "status": "ok",
        "reference_audio": str(ref) if ref else None,
    }


def _benchmark_requested(request: Request) -> bool:
    return request.headers.get("x-benchmark", "").lower() in ("1", "true", "yes")


@app.post("/tts")
def tts_audio(body: TTSRequest, request: Request) -> StreamingResponse:
    try:
        _path_str = str(resolve_speaker_file(body.speaker_wav))
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=400,
            detail=(
                f"{e}. Place sai_audio.m4a at the PersonaRAG repo root, or run "
                f"`python scripts/prepare_reference.py`, or set CLEAN_TTS_SPEAKER."
            ),
        ) from e

    bench = _benchmark_requested(request)
    t0 = time.perf_counter()
    try:
        engine = get_engine()
        rel_arg = body.speaker_wav
        if bench:
            audio, prof = engine.synthesize(
                text=body.text.strip(),
                speaker_wav=rel_arg,
                language=body.language,
                profile=True,
            )
        else:
            audio = engine.synthesize(
                text=body.text.strip(),
                speaker_wav=rel_arg,
                language=body.language,
            )
            prof = None
    except Exception as e:
        logger.exception("TTS failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

    t_after_syn = time.perf_counter()
    sr = engine.output_sample_rate
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format="WAV", subtype="PCM_16")
    buf.seek(0)
    t_end = time.perf_counter()
    wav_s = t_end - t_after_syn
    route_s = t_end - t0
    logger.info(
        "xtts_timing route wav_encode_s=%.3f route_total_s=%.3f sample_rate=%s",
        wav_s,
        route_s,
        sr,
    )
    headers: dict[str, str] = {"Cache-Control": "no-store"}
    if bench and prof is not None:
        headers["X-Benchmark-Conditioning-S"] = f"{prof['conditioning_s']:.6f}"
        headers["X-Benchmark-Generation-S"] = f"{prof['generation_s']:.6f}"
        headers["X-Benchmark-Engine-Total-S"] = f"{prof['engine_total_s']:.6f}"
        headers["X-Benchmark-Conditioning-Cached"] = "1" if prof["conditioning_cached"] else "0"
        headers["X-Benchmark-Wav-Encode-S"] = f"{wav_s:.6f}"
        headers["X-Benchmark-Route-Total-S"] = f"{route_s:.6f}"
    return StreamingResponse(buf, media_type="audio/wav", headers=headers)
