#!/usr/bin/env python3
"""
One-shot synthesis: loads model, writes outputs/demo.wav.
Uses samples/voice.wav if present, else repo-root sai_audio.m4a.

Run from clean-tts/: python scripts/synthesize_once.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.engine import get_engine
from app.paths import OUTPUTS_DIR, default_speaker_path


def main() -> None:
    ref = default_speaker_path()
    if ref is None:
        print(
            "No reference audio found. Either:\n"
            f"  - Place sai_audio.m4a at {ROOT.parent}/\n"
            "  - Or run: python scripts/prepare_reference.py\n"
            "  - Or add clean-tts/samples/voice.wav"
        )
        sys.exit(1)

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUTS_DIR / "demo.wav"

    engine = get_engine()
    engine.synthesize_to_file(
        text="Hello, this is a local XTTS test on Apple Silicon.",
        out_path=str(out),
        speaker_wav=None,
        language="en",
    )
    print(f"Using reference: {ref}")
    print(f"Wrote {out}")
    print("Play: afplay outputs/demo.wav")


if __name__ == "__main__":
    main()
