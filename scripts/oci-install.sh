#!/usr/bin/env bash
#
# Run ON THE UBUNTU VM after SSH (not from your laptop automation).
#
# From your machine:
#   ssh -i /path/to/your_key.pem ubuntu@YOUR_PUBLIC_IP
#
# On the VM (copy-paste block at bottom of this file), or:
#   curl -fsSL https://raw.githubusercontent.com/YOUR_USER/sai-s-PersonaRAG/main/scripts/oci-install.sh | bash
#   (only after you trust the URL; cloning first is safer)
#
set -euo pipefail

REPO_DIR="${PERSONARAG_DIR:-$HOME/sai-s-PersonaRAG}"
GIT_URL="${PERSONARAG_GIT_URL:-https://github.com/saitejareddi3636/sai-s-PersonaRAG.git}"
OLLAMA_CHAT="${OLLAMA_CHAT_MODEL:-qwen2.5:3b}"
OLLAMA_EMBED="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"

have_docker() {
  command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1
}

install_packages_and_docker() {
  echo "==> Updating apt and installing prerequisites..."
  sudo apt-get update -qq
  sudo apt-get install -y ca-certificates curl git gnupg

  if have_docker; then
    echo "==> Docker + Compose already present."
    return
  fi

  echo "==> Installing Docker Engine + Compose plugin (official repo)..."
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg
  # shellcheck source=/dev/null
  . /etc/os-release
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
  sudo apt-get update -qq
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  sudo usermod -aG docker "${SUDO_USER:-$USER}" 2>/dev/null || true
  echo ""
  echo "NOTE: For docker without sudo, log out and SSH in again, or run: newgrp docker"
  echo ""
}

docker_compose() {
  if docker info >/dev/null 2>&1; then
    docker compose "$@"
  else
    sudo docker compose "$@"
  fi
}

install_packages_and_docker

if [[ ! -d "$REPO_DIR/.git" ]]; then
  echo "==> Cloning repo into $REPO_DIR"
  git clone "$GIT_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"
echo "==> Updating git (optional pull)"
git pull --ff-only || true

if [[ ! -f backend/.env ]]; then
  echo "==> Creating backend/.env from example (edit for production)"
  cp backend/.env.example backend/.env
fi

echo "==> Building and starting Ollama + API"
docker_compose up -d --build ollama backend

echo "==> Waiting for Ollama API..."
for _ in $(seq 1 90); do
  if curl -sf http://127.0.0.1:11434/api/tags >/dev/null; then
    break
  fi
  sleep 2
done

echo "==> Pulling Ollama models (chat + embeddings) — may take several minutes..."
docker_compose exec -T ollama ollama pull "$OLLAMA_CHAT"
docker_compose exec -T ollama ollama pull "$OLLAMA_EMBED"

echo "==> Building RAG chunk index"
docker_compose exec -T backend python -m app.rag.ingest --repo-root /app

echo "==> Restarting backend to load chunks"
docker_compose restart backend

sleep 3
echo ""
echo "==> Health check"
curl -sf "http://127.0.0.1:8000/health" && echo "" || echo "Health incomplete yet; check: docker compose logs backend"

echo ""
echo "Done."
echo "  API:  http://$(curl -fsL ifconfig.me 2>/dev/null || echo YOUR_PUBLIC_IP):8000"
echo "  Open OCI ingress: TCP 8000 (and optional 11434 only if you need Ollama from outside)."
echo "  Vercel: NEXT_PUBLIC_API_BASE_URL + BACKEND_ORIG = http://YOUR_PUBLIC_IP:8000"
echo "  CORS: add repo-root .env with CORS_ORIGINS=https://your-app.vercel.app then: docker compose up -d backend"
