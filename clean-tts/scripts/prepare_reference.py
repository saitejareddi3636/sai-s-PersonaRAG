#!/usr/bin/env python3
"""
Convert repo-root sai_audio.m4a -> clean-tts/samples/voice.wav (mono, 24 kHz, 16-bit).
Requires ffmpeg on PATH (`brew install ffmpeg`).

Run from clean-tts/: python scripts/prepare_reference.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent
SRC = REPO_ROOT / "sai_audio.m4a"
OUT = ROOT / "samples" / "voice.wav"


def main() -> int:
    if not SRC.is_file():
        print(f"Missing source: {SRC}")
        return 1
    if shutil.which("ffmpeg") is None:
        print("ffmpeg not found. Install: brew install ffmpeg")
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(SRC),
        "-ar",
        "24000",
        "-ac",
        "1",
        "-sample_fmt",
        "s16",
        str(OUT),
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
