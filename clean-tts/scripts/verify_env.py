#!/usr/bin/env python3
"""Run after: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"""

from __future__ import annotations

import subprocess
import sys


def main() -> None:
    print("python:", sys.version)
    try:
        import torch

        print("torch:", torch.__version__)
        print("MPS available:", torch.backends.mps.is_available())
    except Exception as e:
        print("torch:", "NOT OK", e)

    try:
        import TTS

        print("TTS:", getattr(TTS, "__version__", "unknown"))
    except Exception as e:
        print("TTS:", "NOT OK", e)
        return

    try:
        r = subprocess.run(
            ["tts", "--list_models"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        lines = [ln for ln in r.stdout.splitlines() if "xtts" in ln.lower()]
        print("models matching 'xtts':")
        for ln in lines[:20]:
            print(" ", ln)
        if not lines:
            print("  (none found — check TTS install)")
    except Exception as e:
        print("tts --list_models:", e)


if __name__ == "__main__":
    main()
