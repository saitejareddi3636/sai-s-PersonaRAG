#!/usr/bin/env python3
"""Run ingestion from the repository root: python scripts/ingest.py"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.rag.ingest import main  # noqa: E402


if __name__ == "__main__":
    main()
