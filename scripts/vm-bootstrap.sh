#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Building & starting Ollama + backend (no local Next container — use Vercel)"
docker compose up -d --build ollama backend

echo "==> Wait for Ollama to accept API..."
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:11434/api/tags >/dev/null; then
    break
  fi
  sleep 2
done

echo "==> Pull chat + embed models (adjust names if needed)"
docker exec personarag-ollama ollama pull "${OLLAMA_CHAT_MODEL:-qwen2.5:3b}" || true
docker exec personarag-ollama ollama pull "${OLLAMA_EMBED_MODEL:-nomic-embed-text}" || true

echo "==> Build chunk index inside backend container"
docker exec personarag-backend python -m app.rag.ingest --repo-root /app || {
  echo "Ingest failed — ensure ./data/raw has markdown on the host."
  exit 1
}

echo "==> Restart backend to load new chunks"
docker compose restart backend

echo "Done. Health: curl -sf http://127.0.0.1:8000/health | jq ."
echo "Open OCI security list: TCP 8000 from Vercel (or 0.0.0.0/0 for testing)."
echo "Repo-root CORS: cp compose.env.example .env && edit CORS_ORIGINS -> your Vercel URL, then docker compose up -d backend"
echo "Vercel env: NEXT_PUBLIC_API_BASE_URL=http://YOUR_PUBLIC_IP:8000"
echo "             BACKEND_ORIG=http://YOUR_PUBLIC_IP:8000   (same value; rewrite target)"
