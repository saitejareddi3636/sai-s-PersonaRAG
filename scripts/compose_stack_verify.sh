#!/usr/bin/env bash
# Build and smoke-test the stack like a small cloud: Ollama + backend, then verify LLM/STT/TTS
# from inside the backend container. Run from repo root.
#
#   chmod +x scripts/compose_stack_verify.sh
#   ./scripts/compose_stack_verify.sh
#
# First run pulls the chat model (slow). Set SKIP_OLLAMA_PULL=1 to skip pull if already cached.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose)
if ! docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
fi

MODEL="${OLLAMA_CHAT_MODEL:-qwen2.5:3b}"

echo "== docker build backend =="
"${COMPOSE[@]}" build backend

echo "== up ollama + backend =="
"${COMPOSE[@]}" up -d ollama backend

echo "== wait for Ollama health =="
for _ in $(seq 1 45); do
  if "${COMPOSE[@]}" exec -T ollama ollama list >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if [[ "${SKIP_OLLAMA_PULL:-0}" != "1" ]]; then
  echo "== ollama pull ${MODEL} (idempotent) =="
  "${COMPOSE[@]}" exec -T ollama ollama pull "${MODEL}"
fi

echo "== wait for backend /health =="
for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "== verify LLM + STT + TTS inside backend container =="
"${COMPOSE[@]}" exec -T backend python scripts/verify_local_stack.py

echo ""
echo "== OK: compose stack verified =="
