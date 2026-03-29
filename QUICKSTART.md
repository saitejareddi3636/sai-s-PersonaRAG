# Quick Start Guide: Ollama + Qwen 2.5 Stack

## 🚀 Fastest Way to Run (Docker)

```bash
cd sai-s-PersonaRAG
docker compose up --build

# Wait for "Successfully started ollama" message
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Ollama: http://localhost:11434
```

**First run**: Models will download automatically (~2.3 GB total)

---

## 🛠️ Local Development (No Docker)

### 1. Install Ollama
- **macOS**: `brew install ollama`
- **Linux/Windows**: Download from https://ollama.ai

### 2. Start Ollama & Pull Models
```bash
# Terminal 1: Start Ollama daemon
ollama serve

# Terminal 2: Pull models (one-time)
ollama pull qwen2.5:3b
ollama pull nomic-embed-text

# Verify
ollama list
```

### 3. Run Backend
```bash
# Terminal 3
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run Frontend
```bash
# Terminal 4
cd frontend
npm install
npm run dev

# Open http://localhost:3000
```

---

## ✅ Verify Everything is Working

```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check Backend
curl http://localhost:8000/health

# Try a chat query
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is your experience?"}'
```

---

## 🔧 Environment Variables

Defaults work fine! Optional customizations:

```bash
# backend/.env (copy from .env.example)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:3b
OLLAMA_EMBED_MODEL=nomic-embed-text
RETRIEVAL_BACKEND=auto              # or "tfidf" or "ollama"
RETRIEVAL_TOP_K=5
```

---

## 🐳 Docker Compose Services

| Service | Port | URL |
|---------|------|-----|
| Ollama | 11434 | http://localhost:11434 |
| Backend (FastAPI) | 8000 | http://localhost:8000 |
| Frontend (Next.js) | 3000 | http://localhost:3000 |

---

## 🎯 Use Different Models

Edit `docker-compose.yml` or `.env`:

```bash
# Faster (less accurate)
OLLAMA_CHAT_MODEL=neural-chat:latest  # ~4GB
OLLAMA_EMBED_MODEL=bge-small-en-v1.5:latest

# Better quality (slower)
OLLAMA_CHAT_MODEL=mistral:latest      # ~5GB
OLLAMA_EMBED_MODEL=bge-base-en-v1.5:latest

# For GPU (fast)
OLLAMA_CHAT_MODEL=qwen2.5:14b         # ~9GB (needs GPU)
```

Pull new models:
```bash
ollama pull <model-name>
```

---

## 📊 Performance Tips

| Backend | Speed | Quality | RAM | Notes |
|---------|-------|---------|-----|-------|
| **TF-IDF** | ⚡ 50ms | ⭐⭐ | 100MB | Keyword search, fast fallback |
| **Ollama (CPU)** | 🐢 1-3s | ⭐⭐⭐⭐ | 4GB | Semantic, good quality |
| **Ollama (GPU)** | 🚀 200-500ms | ⭐⭐⭐⭐ | 8GB | Best performance |

Switch to TF-IDF if Ollama is slow:
```bash
RETRIEVAL_BACKEND=tfidf  # Falls back to keyword search
```

---

## 🧪 Run Tests

```bash
cd backend
pytest                          # All tests
pytest -v                       # Verbose
pytest -k test_chat             # Specific test
pytest --cov=app tests/         # Coverage
```

---

## 🐛 Troubleshooting

### Ollama won't start
```bash
# Check if running
curl http://localhost:11434/api/tags

# If not, manually start
ollama serve

# Or restart service
brew services restart ollama  # macOS
```

### Backend can't connect to Ollama
```bash
# Verify URL is correct
echo $OLLAMA_BASE_URL  # Should be http://localhost:11434

# Check Docker network (if using compose)
docker network inspect personarag-network
```

### Models not downloaded
```bash
ollama list                  # See what's installed
ollama pull qwen2.5:3b      # Download specific model
```

### Slow responses
1. **First request after startup**: Normal (model loads)
2. **On CPU**: Expected (1-3s per query)
3. **Out of memory**: Use smaller model or TF-IDF backend

---

## 📖 Detailed Documentation

- [Full Setup Guide](README.md#getting-started)
- [Architecture](docs/architecture.md)
- [Docker Setup](docs/DOCKER_SETUP.md)
- [Migration Summary](MIGRATION_SUMMARY.md)

---

## 🎉 Done!

You should now have a fully working, local RAG chatbot powered by Ollama and Qwen 2.5. No external APIs, no API keys needed.

Questions? Check the [troubleshooting section](README.md#troubleshooting) or review the logs:

```bash
docker compose logs backend
docker compose logs ollama
```
