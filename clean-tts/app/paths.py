from __future__ import annotations

import os
from pathlib import Path

# clean-tts/ root (this subproject)
ROOT = Path(__file__).resolve().parent.parent
# PersonaRAG repo root (parent of clean-tts/)
REPO_ROOT = ROOT.parent
SAMPLES_DIR = ROOT / "samples"
OUTPUTS_DIR = ROOT / "outputs"
SAMPLE_VOICE_WAV = SAMPLES_DIR / "voice.wav"
# Your reference clip at repo root (as requested)
REPO_REFERENCE_M4A = REPO_ROOT / "sai_audio.m4a"


def default_speaker_path() -> Path | None:
    """
    Prefer converted WAV in samples/; else use repo-root sai_audio.m4a if present.
    Override: set CLEAN_TTS_SPEAKER to an absolute path.
    """
    override = os.environ.get("CLEAN_TTS_SPEAKER", "").strip()
    if override:
        p = Path(override).expanduser().resolve()
        return p if p.is_file() else None

    if SAMPLE_VOICE_WAV.is_file():
        return SAMPLE_VOICE_WAV.resolve()
    if REPO_REFERENCE_M4A.is_file():
        return REPO_REFERENCE_M4A.resolve()
    return None


def default_speaker_rel_for_display() -> str:
    """Short label for errors/logs."""
    if SAMPLE_VOICE_WAV.is_file():
        return "samples/voice.wav"
    if REPO_REFERENCE_M4A.is_file():
        try:
            return str(REPO_REFERENCE_M4A.relative_to(REPO_ROOT))
        except ValueError:
            return str(REPO_REFERENCE_M4A)
    return "(none)"


def resolve_speaker_file(speaker_wav: str | None) -> Path:
    """Path to reference audio for Coqui. speaker_wav is relative to clean-tts/ or an absolute path."""
    if speaker_wav:
        p = (ROOT / speaker_wav).resolve()
        if not p.is_file():
            p = Path(speaker_wav).expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(f"Speaker audio not found: {speaker_wav}")
        return p
    default = default_speaker_path()
    if default is None or not default.is_file():
        raise FileNotFoundError(
            "No reference audio. Add clean-tts/samples/voice.wav, or place sai_audio.m4a at the "
            "PersonaRAG repo root, or run scripts/prepare_reference.py, or set CLEAN_TTS_SPEAKER."
        )
    return default
