from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    for key in ("REPO_ROOT", "INGEST_REPO_ROOT"):
        v = os.environ.get(key, "").strip()
        if v:
            return Path(v).resolve()
    return Path(__file__).resolve().parents[3]


def default_chunks_json_path() -> Path:
    return repo_root() / "data" / "processed" / "chunks.json"
