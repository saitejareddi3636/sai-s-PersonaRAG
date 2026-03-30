#!/usr/bin/env bash
# Quick HTTP check when clean-tts is already running (e.g. ./run.sh or uvicorn on 8010).
set -euo pipefail
BASE="${1:-http://127.0.0.1:8010}"
echo "GET ${BASE}/health"
curl -sfS "${BASE}/health" | head -c 400
echo ""
OUT="${TMPDIR:-/tmp}/clean_tts_http_test.wav"
echo "POST ${BASE}/tts -> ${OUT}"
curl -sfS -X POST "${BASE}/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"Quick HTTP test.","language":"en"}' \
  -o "${OUT}"
ls -la "${OUT}"
echo "OK — play: afplay ${OUT}"
