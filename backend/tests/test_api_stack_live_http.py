"""
Live HTTP checks against a running API (optional).

  LIVE_API_BASE=http://127.0.0.1:8000 pytest tests/test_api_stack_live_http.py -v -s

`test_live_stack_script_streams_output` runs `scripts/check_stack.py` with **stdout not
captured**, so you see health / chat / TTS / STT / stream lines on the terminal.

Skips automatically when LIVE_API_BASE is unset (see short summary from `pytest -ra`).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = BACKEND_ROOT / "scripts" / "check_stack.py"


@pytest.mark.skipif(
    not os.environ.get("LIVE_API_BASE"),
    reason="Set LIVE_API_BASE (e.g. http://127.0.0.1:8000) to run live stack tests.",
)
def test_live_stack_script_streams_output() -> None:
    """Runs check_stack.py with output on your terminal (not captured)."""
    base = os.environ["LIVE_API_BASE"].rstrip("/")
    print(f"\n>>> Running scripts/check_stack.py against {base} ...\n", flush=True)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--base-url", base],
        cwd=str(BACKEND_ROOT),
        timeout=600,
    )
    assert proc.returncode == 0, (
        f"check_stack.py exited {proc.returncode}. "
        "Fix health/chat/TTS/STT/stream on the API, then re-run with LIVE_API_BASE set."
    )
