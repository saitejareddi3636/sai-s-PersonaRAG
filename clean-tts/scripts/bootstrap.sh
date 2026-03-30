#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MIN_FREE_GB="${MIN_FREE_GB:-8}"
avail_kb=$(df -k "$ROOT" | awk 'NR==2 {print $4}')
avail_gb=$((avail_kb / 1024 / 1024))
if [[ "$avail_gb" -lt "$MIN_FREE_GB" ]]; then
  echo "ERROR: Low disk space (~${avail_gb} GiB free under $ROOT)."
  echo "       Need at least ~${MIN_FREE_GB} GiB free for PyTorch + Coqui TTS + models."
  echo "       Free space (Empty Trash, delete large downloads, Xcode simulators, Docker images), then retry."
  exit 1
fi

PY="${PYTHON:-python3.11}"
if ! command -v "$PY" &>/dev/null; then
  PY="python3"
fi

"$PY" -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools

# Pre-install heavy / flaky wheels first (reduces parallel build races)
pip install gruut-lang-es gruut-lang-fr || true

pip install -r requirements.txt

echo "OK. Next: add samples/voice.wav, then: python scripts/verify_env.py"
