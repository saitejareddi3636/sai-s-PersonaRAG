"""
Live HTTP checks against a running API (optional).

  LIVE_API_BASE=http://127.0.0.1:8000 pytest backend/tests/test_api_stack_live_http.py -v

Skips automatically when LIVE_API_BASE is unset.
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
def test_live_stack_script_exits_zero() -> None:
    base = os.environ["LIVE_API_BASE"].rstrip("/")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--base-url", base],
        cwd=str(BACKEND_ROOT),
        capture_output=True,
        text=True,
        timeout=600,
    )
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    assert proc.returncode == 0, f"check_stack.py failed with {proc.returncode}"
