#!/usr/bin/env python3
"""
Standalone XTTS smoke test (no PersonaRAG API). Run from clean-tts with venv active:

  cd clean-tts && source .venv/bin/activate && python scripts/quick_test_tts.py

Writes outputs/quick_test.wav on success (exit 0).
"""
from __future__ import annotations

import os
import sys

# Project root = clean-tts/
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def main() -> int:
    import logging

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    out_dir = os.path.join(_ROOT, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "quick_test.wav")

    from app.engine import get_engine

    print("Loading model + reference speaker (first run can take a while)...")
    eng = get_engine()
    eng.synthesize_to_file(
        "Hello. This is a quick clean T T S test.",
        out_path=out_path,
        language="en",
    )

    size = os.path.getsize(out_path)
    if size < 200:
        print(f"FAIL: output too small ({size} bytes): {out_path}")
        return 1

    print(f"OK — wrote {out_path} ({size} bytes)")
    print("Play:  afplay outputs/quick_test.wav   # macOS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
