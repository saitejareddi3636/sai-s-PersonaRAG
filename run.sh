#!/usr/bin/env bash
# Starts API + Next.js with Piper as default TTS.
# - No uvicorn --reload on the API unless DEV_RELOAD=1
# - Next uses webpack dev on 127.0.0.1
# - Default TTS provider is Piper (TTS_PROVIDER=piper unless already set)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$ROOT/backend/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
  echo "Run ./setup.sh once first (creates venv and installs deps)."
  exit 1
fi
[[ -f "$ROOT/frontend/.env.local" ]] || cp "$ROOT/frontend/.env.example" "$ROOT/frontend/.env.local"
[[ -f "$ROOT/backend/.env" ]] || cp "$ROOT/backend/.env.example" "$ROOT/backend/.env"

stop_stale_listener() {
  local port="$1"
  local pids=""
  pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "Port $port already in use; stopping stale process(es): $pids"
    # shellcheck disable=SC2086
    kill $pids 2>/dev/null || true
    sleep 0.5
  fi
}

# Clean stale local dev listeners so reruns do not fail with bind/next lock errors.
stop_stale_listener 3000
stop_stale_listener 3001
stop_stale_listener 8000

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

export TTS_PROVIDER="${TTS_PROVIDER:-piper}"
echo "Using TTS_PROVIDER=${TTS_PROVIDER}."

cd "$ROOT/backend"
# Avoid "${array[@]}" when empty — macOS bash 3.2 + set -u errors ("unbound variable").
if [[ "${DEV_RELOAD:-}" == "1" ]]; then
  "$PY" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --log-level warning &
else
  "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level warning &
fi
BACKEND_PID=$!

cd "$ROOT/frontend"
echo ""
echo "Frontend:    http://127.0.0.1:3000"
echo "API health:  http://127.0.0.1:8000/health"
echo "Press Ctrl+C to stop all servers started here."
echo ""
npm run dev:light
