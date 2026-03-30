#!/usr/bin/env bash
# API only (one process). Use when the UI is not needed or run frontend elsewhere.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$ROOT/backend/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "Run ./setup.sh first."
  exit 1
fi
[[ -f "$ROOT/backend/.env" ]] || cp "$ROOT/backend/.env.example" "$ROOT/backend/.env"

RELOAD=""
if [[ "${DEV_RELOAD:-}" == "1" ]]; then
  RELOAD="--reload"
fi

cd "$ROOT/backend"
echo "API: http://127.0.0.1:8000/health  (Ctrl+C to stop)"
echo "Tip: omit file watchers — do not set DEV_RELOAD=1 unless you need auto-restart."
exec "$PY" -m uvicorn app.main:app $RELOAD --host 127.0.0.1 --port 8000 --log-level warning
