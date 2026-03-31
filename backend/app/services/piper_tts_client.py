import asyncio
import logging
import os
import tempfile
import wave
from pathlib import Path

logger = logging.getLogger(__name__)


class PiperTTSClient:
    def __init__(
        self,
        *,
        piper_binary: str,
        model_path: str,
        speaker_id: int | None = None,
        synth_timeout_s: float = 45.0,
    ):
        self.piper_binary = piper_binary
        self.model_path = model_path
        self.speaker_id = speaker_id
        self.synth_timeout_s = synth_timeout_s

    async def synthesize(self, text: str) -> dict:
        prompt = (text or "").strip()
        if not prompt:
            return {
                "success": False,
                "audio_url": None,
                "audio_path": None,
                "duration_ms": None,
                "provider": "piper",
                "message": "Empty text",
            }

        if not self.model_path:
            return {
                "success": False,
                "audio_url": None,
                "audio_path": None,
                "duration_ms": None,
                "provider": "piper",
                "message": "PIPER_MODEL_PATH is not set.",
            }

        if not Path(self.model_path).exists():
            return {
                "success": False,
                "audio_url": None,
                "audio_path": None,
                "duration_ms": None,
                "provider": "piper",
                "message": f"Piper model not found: {self.model_path}",
            }

        args = [self.piper_binary, "--model", self.model_path]
        if self.speaker_id is not None:
            args.extend(["--speaker", str(self.speaker_id)])

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as out:
            args.extend(["--output_file", out.name])
            env = os.environ.copy()

            try:
                proc = await asyncio.create_subprocess_exec(
                    *args,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env,
                )
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(input=prompt.encode("utf-8")),
                    timeout=self.synth_timeout_s,
                )
            except FileNotFoundError:
                return {
                    "success": False,
                    "audio_url": None,
                    "audio_path": None,
                    "duration_ms": None,
                    "provider": "piper",
                    "message": f"Piper binary not found: {self.piper_binary}",
                }
            except TimeoutError:
                return {
                    "success": False,
                    "audio_url": None,
                    "audio_path": None,
                    "duration_ms": None,
                    "provider": "piper",
                    "message": "Piper synthesis timed out.",
                }

            if proc.returncode != 0:
                detail = (stderr or stdout or b"").decode("utf-8", errors="ignore").strip()
                return {
                    "success": False,
                    "audio_url": None,
                    "audio_path": None,
                    "duration_ms": None,
                    "provider": "piper",
                    "message": f"Piper synthesis failed: {detail or f'exit {proc.returncode}'}",
                }

            wav_bytes = Path(out.name).read_bytes()
            duration_ms = _wav_duration_ms(wav_bytes)
            logger.info("voice_tts_piper chars=%s duration_ms=%s", len(prompt), duration_ms)
            return {
                "success": True,
                "audio_url": None,
                "audio_wav_bytes": wav_bytes,
                "audio_path": None,
                "duration_ms": duration_ms,
                "provider": "piper",
                "message": None,
            }


def _wav_duration_ms(wav_bytes: bytes) -> int | None:
    try:
        import io

        with wave.open(io.BytesIO(wav_bytes)) as wf:
            frames = wf.getnframes()
            rate = wf.getframerate() or 22050
            return int(round(frames / float(rate) * 1000))
    except Exception:
        return None
