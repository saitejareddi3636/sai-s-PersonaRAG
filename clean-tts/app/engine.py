from __future__ import annotations

import logging
import os
import time
from typing import Any, TypedDict

import numpy as np


class SynthesizeProfile(TypedDict):
    conditioning_s: float
    conditioning_cached: bool
    generation_s: float
    engine_total_s: float

# Coqui XTTS otherwise prompts [y/n] on stdin — unusable for an API server.
# You agree to CPML / license terms when using the model: https://coqui.ai/cpml
os.environ.setdefault("COQUI_TOS_AGREED", "1")

from app.paths import resolve_speaker_file

logger = logging.getLogger(__name__)

MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"


def _patch_torch_load_for_coqui_checkpoints() -> None:
    """PyTorch 2.6+ defaults torch.load(weights_only=True); Coqui XTTS checkpoints need full unpickle."""
    import torch

    if getattr(torch.load, "_coqui_personarag_patch", False):
        return
    _orig = torch.load

    def _wrapped(*args, **kwargs):
        kwargs["weights_only"] = False
        try:
            return _orig(*args, **kwargs)
        except TypeError:
            kwargs.pop("weights_only", None)
            return _orig(*args, **kwargs)

    setattr(_wrapped, "_coqui_personarag_patch", True)
    torch.load = _wrapped  # type: ignore[method-assign]


class XTTSEngine:
    """Loads XTTS v2 once; caches speaker conditioning latents per reference path; reuses model for all requests."""

    def __init__(self, device: str | None = None) -> None:
        self._model: Any = None
        self._device = device
        # Resolved absolute speaker path -> (gpt_cond_latent, speaker_embedding) on CPU
        self._latent_cache: dict[str, tuple[Any, Any]] = {}

    def _pick_device(self) -> str:
        if self._device:
            return self._device
        try:
            import torch

            if torch.backends.mps.is_available():
                return "mps"
        except Exception:
            pass
        return "cpu"

    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        _patch_torch_load_for_coqui_checkpoints()
        from TTS.api import TTS

        dev = self._pick_device()
        t0 = time.perf_counter()
        logger.info("Loading XTTS model=%s device=%s", MODEL_NAME, dev)
        tts = TTS(model_name=MODEL_NAME)
        try:
            tts = tts.to(dev)
        except Exception as e:
            logger.warning("Device %s failed (%s); using CPU.", dev, e)
            tts = tts.to("cpu")
        self._model = tts
        logger.info("xtts_timing model_load_s=%.3f device_reported=%s", time.perf_counter() - t0, dev)

    def _xtts_and_config(self) -> tuple[Any, Any]:
        assert self._model is not None
        syn = self._model.synthesizer
        return syn.tts_model, syn.tts_config

    def _get_or_build_latents(self, audio_path: str) -> tuple[Any, Any, float, bool]:
        """Return (gpt_cond_latent, speaker_embedding, conditioning_s, cache_hit)."""
        key = os.path.abspath(audio_path)
        xtts, config = self._xtts_and_config()
        device = xtts.device

        t0 = time.perf_counter()
        if key in self._latent_cache:
            gpt_c, spk = self._latent_cache[key]
            gpt_c = gpt_c.to(device)
            spk = spk.to(device)
            dt = time.perf_counter() - t0
            logger.info(
                "xtts_timing conditioning_s=%.3f (cached path=%s)",
                dt,
                os.path.basename(key),
            )
            return gpt_c, spk, dt, True

        gpt_c, spk = xtts.get_conditioning_latents(
            audio_path=audio_path,
            gpt_cond_len=config.gpt_cond_len,
            gpt_cond_chunk_len=config.gpt_cond_chunk_len,
            max_ref_length=config.max_ref_len,
            sound_norm_refs=config.sound_norm_refs,
        )
        self._latent_cache[key] = (gpt_c.detach().cpu(), spk.detach().cpu())
        gpt_c = gpt_c.to(device)
        spk = spk.to(device)
        dt = time.perf_counter() - t0
        logger.info(
            "xtts_timing conditioning_s=%.3f (computed path=%s)",
            dt,
            os.path.basename(key),
        )
        return gpt_c, spk, dt, False

    def warm_speaker_file(self, audio_path: str) -> None:
        """Preload model (if needed) and conditioning latents for one reference file."""
        self._ensure_model()
        path = str(audio_path)
        if not os.path.isfile(path):
            logger.warning("warm_speaker_file: missing %s", path)
            return
        self._get_or_build_latents(path)
        logger.info("xtts warm_speaker_file ok: %s", path)

    def synthesize(
        self,
        text: str,
        speaker_wav: str | None = None,
        language: str = "en",
        *,
        split_sentences: bool = True,
        profile: bool = False,
    ) -> Any | tuple[Any, SynthesizeProfile]:
        """Return numpy float32 waveform, or (wav, profile) when profile=True."""
        self._ensure_model()
        path = str(resolve_speaker_file(speaker_wav))
        syn = self._model.synthesizer
        xtts, config = self._xtts_and_config()

        if not hasattr(xtts, "get_conditioning_latents"):
            logger.warning("Model is not XTTS; falling back to TTS.tts() (no latent cache).")
            wav = self._model.tts(
                text=text,
                speaker_wav=path,
                language=language,
                split_sentences=split_sentences,
            )
            if profile:
                prof: SynthesizeProfile = {
                    "conditioning_s": 0.0,
                    "conditioning_cached": False,
                    "generation_s": 0.0,
                    "engine_total_s": 0.0,
                }
                return wav, prof
            return wav

        t_req = time.perf_counter()
        gpt_cond, spk_emb, conditioning_s, cond_cached = self._get_or_build_latents(path)

        settings = {
            "temperature": config.temperature,
            "length_penalty": config.length_penalty,
            "repetition_penalty": config.repetition_penalty,
            "top_k": config.top_k,
            "top_p": config.top_p,
        }

        sentences = syn.split_into_sentences(text) if split_sentences else [text]
        if split_sentences and len(sentences) > 1:
            logger.info("xtts text sentences=%s", len(sentences))

        t_gen0 = time.perf_counter()
        pieces: list[np.ndarray] = []
        for sen in sentences:
            s = sen.strip()
            if not s:
                continue
            out = xtts.inference(s, language, gpt_cond, spk_emb, **settings)
            w = np.asarray(out["wav"], dtype=np.float32).reshape(-1)
            pieces.append(w)

        if not pieces:
            wav = np.array([], dtype=np.float32)
        else:
            wav = np.concatenate(pieces) if len(pieces) > 1 else pieces[0]
        t_gen = time.perf_counter() - t_gen0
        engine_total = time.perf_counter() - t_req
        logger.info(
            "xtts_timing generation_s=%.3f sentences=%s chars=%s",
            t_gen,
            len(pieces),
            len(text),
        )
        logger.info(
            "xtts_timing request_total_s=%.3f (after conditioning; excludes model load)",
            engine_total,
        )
        if profile:
            return wav, {
                "conditioning_s": conditioning_s,
                "conditioning_cached": cond_cached,
                "generation_s": t_gen,
                "engine_total_s": engine_total,
            }
        return wav

    @property
    def output_sample_rate(self) -> int:
        self._ensure_model()
        return int(self._model.synthesizer.output_sample_rate)

    def synthesize_to_file(
        self,
        text: str,
        out_path: str,
        speaker_wav: str | None = None,
        language: str = "en",
    ) -> None:
        self._ensure_model()
        wav = self.synthesize(text, speaker_wav=speaker_wav, language=language, split_sentences=True)
        import soundfile as sf

        sf.write(out_path, wav, self.output_sample_rate, format="WAV", subtype="PCM_16")


_engine: XTTSEngine | None = None


def get_engine() -> XTTSEngine:
    global _engine
    if _engine is None:
        _engine = XTTSEngine()
    return _engine
