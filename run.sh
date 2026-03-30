#!/usr/bin/env bash
# Starts clean-tts (voice) + API + Next.js in one terminal when possible.
# - No uvicorn --reload on the API unless DEV_RELOAD=1
# - Next uses webpack dev on 127.0.0.1
# - Set START_VOICE=0 to skip launching clean-tts (uses backend/.env TTS only)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$ROOT/backend/.venv/bin/python"
CT_PY="$ROOT/clean-tts/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
  echo "Run ./setup.sh once first (creates venv and installs deps)."
  exit 1
fi
[[ -f "$ROOT/frontend/.env.local" ]] || cp "$ROOT/frontend/.env.example" "$ROOT/frontend/.env.local"
[[ -f "$ROOT/backend/.env" ]] || cp "$ROOT/backend/.env.example" "$ROOT/backend/.env"

CLEAN_TTS_PID=""
start_clean_tts() {
  if [[ "${START_VOICE:-1}" != "1" ]]; then
    echo "START_VOICE=0 — not starting clean-tts; using TTS settings from backend/.env"
    return 0
  fi
  if command -v lsof >/dev/null 2>&1 && lsof -i :8010 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port 8010 already in use — using existing service as clean-tts."
    export TTS_PROVIDER=clean-xtts
    export CLEAN_TTS_URL=http://127.0.0.1:8010
    return 0
  fi
  if [[ ! -x "$CT_PY" ]]; then
    echo "No clean-tts venv at clean-tts/.venv — Voice uses backend/.env only."
    echo "For real speech in one command next time: cd clean-tts && follow README (bootstrap), then ./run.sh"
    return 0
  fi
  (
    cd "$ROOT/clean-tts"
    export COQUI_TOS_AGREED=1
    exec "$CT_PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --log-level warning
  ) &
  CLEAN_TTS_PID=$!
  export TTS_PROVIDER=clean-xtts
  export CLEAN_TTS_URL=http://127.0.0.1:8010
  echo "clean-tts: http://127.0.0.1:8010 (voice synthesis)"
  sleep "${VOICE_BOOT_DELAY:-3}"
}

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "${CLEAN_TTS_PID:-}" ]] && kill -0 "$CLEAN_TTS_PID" 2>/dev/null; then
    kill "$CLEAN_TTS_PID" 2>/dev/null || true
    wait "$CLEAN_TTS_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

start_clean_tts

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
echo "clean-tts:   http://127.0.0.1:8010/health"
echo "Press Ctrl+C to stop all servers started here."
echo ""
npm run dev:light
