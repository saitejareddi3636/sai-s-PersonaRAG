# PersonaRAG

A professional AI-powered portfolio web application that answers recruiter questions through retrieval-augmented generation (RAG) over your professional data. Built for accuracy, transparency, and low-latency question answering.

## Overview

**PersonaRAG** is a full-stack application that enables visitors to ask natural-language questions about your skills, experience, and projects. Answers are grounded in your professional content (stored as markdown) and retrieved via semantic search, ensuring information is accurate and verifiable.

**Key characteristics:**
- RAG-based: Answers sourced from indexed professional data
- Session-aware: Multi-turn conversations with bounded history
- Fallback-capable: Works without LLM (excerpt mode) or when Ollama unavailable
- Production-ready: Docker, health checks, structured logging
- Fully local: Qwen 2.5 chat model + nomic-embed-text embeddings, no external APIs
- Future voice-ready: TTS infrastructure placeholder for local synthesis

## Why

Traditional portfolios are static; recruiters can't ask follow-up questions. RAG-powered portfolios solve this by:
- **Accuracy**: No hallucination; all claims backed by your professional data
- **Engagement**: Conversational interface feels natural and premium
- **Verification**: Sources show exactly where answers came from
- **Scalability**: Handles multiple concurrent users and long conversations

## Features

- ✅ **Semantic search** over professional content (TF-IDF or local Ollama embeddings)
- ✅ **Grounded answers** with confidence levels and source citations
- ✅ **Session memory** for multi-turn conversations (bounded, memory-safe)
- ✅ **Local LLM**: Qwen 2.5 (3B) via Ollama (no paid APIs)
- ✅ **Multi-retrieval backend**: TF-IDF (keyword) or Ollama embeddings (semantic)
- ✅ **Fallback mode**: Returns excerpt-based answers if LLM unavailable
- ✅ **Docker Compose setup** for single-command local/remote deployment
- ✅ **Health checks** and structured logging
- 🔄 **Future TTS support**: Placeholder for F5-TTS local voice synthesis

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                  │
│              React | TypeScript | Tailwind              │
└──────────────┬──────────────────────────────────────────┘
               │ HTTP REST
               │
┌──────────────┴──────────────────────────────────────────┐
│                  Backend (FastAPI)                      │
│  ┌──────────────┬──────────────┬──────────────────────┐ │
│  │  Chat Route  │ TTS Route    │  Health / Admin      │ │
│  └──────────────┴──────────────┴──────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  RAG Orchestration & LLM Service                     │ │
│  │  - Retrieve top-k chunks                            │ │
│  │  - Rank by relevance + confidence                   │ │
│  │  - Generate grounded answer (Ollama or excerpt)     │ │
│  └──────────────────────────────────────────────────────┘ │
│  ┌──────────────┬──────────────────┬──────────────────┐  │
│  │ Retrieval    │ Session Store    │ Logging          │  │
│  │ (TF-IDF or   │ (in-memory;      │ (structured)     │  │
│  │  Ollama)     │  Redis-ready)    │                  │  │
│  └──────────────┴──────────────────┴──────────────────┘  │
└──────────────┬──────────────────────────────────────────┘
               │
        ┌──────┴──────┬──────────┐
        │             │          │
    ┌───┴────┐    ┌──┴──┐   ┌──┴──┐
    │chunks. │    │Ollama   │F5-TTS
    │json    │    │Local    │(future)
    └────────┘    └─────┘   └──────┘
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS | Modern web UI |
| **Backend** | FastAPI, Pydantic, httpx | REST API, validation |
| **LLM** | Ollama, Qwen 2.5 (3B) | Local chat model |
| **Embeddings** | Ollama, nomic-embed-text | Local semantic search |
| **Retrieval** | scikit-learn (TF-IDF) | Fallback keyword search |
| **Session** | In-memory dict (Redis-ready) | Conversation history |
| **Data** | Markdown (raw) + JSON (processed) | Source content |
| **Dev** | Docker, Docker Compose, pytest | Containerization & testing |

## Repository Structure

```
.
├── frontend/                   # Next.js application
│   ├── app/                    # Pages (layout, home, chat)
│   ├── components/             # React components (chat UI, sections)
│   ├── lib/                    # Utilities (API client, config)
│   ├── Dockerfile              # Production-optimized build
│   └── package.json
│
├── backend/                    # FastAPI service
│   ├── app/
│   │   ├── api/routes/         # API endpoints (chat.py, tts.py, health.py)
│   │   ├── core/               # Config, logging setup
│   │   ├── rag/                # Retrieval (backends, chunking, retrieve, ingest)
│   │   ├── schemas/            # Pydantic models (chat, tts, retrieval)
│   │   ├── services/           # Business logic (llm_service, tts_service, session_store)
│   │   └── main.py             # FastAPI app factory
│   ├── tests/                  # Test suite
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
│
├── data/
│   ├── raw/                    # Source markdown (8 topic files)
│   │   ├── summary.md
│   │   ├── work_experience.md
│   │   ├── education.md
│   │   ├── projects.md
│   │   ├── skills.md
│   │   ├── achievements.md
│   │   ├── target_roles.md
│   │   └── faq_for_recruiters.md
│   └── processed/
│       ├── chunks.json         # Generated; 2-5min to create
│       └── chunks.sample.json  # Reference output
│
├── scripts/
│   └── ingest.py               # Data ingestion pipeline
│
├── docs/
│   ├── architecture.md         # System design & extension points
│   ├── content_strategy.md     # Data organization & retrieval intent
│   ├── TTS_INTEGRATION_GUIDE.md # F5-TTS integration roadmap
│   └── DOCKER_SETUP.md         # Container development guide
│
├── docker-compose.yml          # Local development environment
├── README.md                   # This file
└── .env.example                # Environment template
```

## Getting Started

### Simplest local run (no Docker)

From the repository root:

```bash
./setup.sh   # one time: Python venv, dependencies, env files
./run.sh     # clean-tts (if installed) + API + Next.js; Ctrl+C stops all
```

Then open [http://127.0.0.1:3000](http://127.0.0.1:3000). Health: [API](http://127.0.0.1:8000/health), [clean-tts](http://127.0.0.1:8010/health) when that service is running.

**Voice in one command:** If `clean-tts/.venv` exists (see [clean-tts/README.md](clean-tts/README.md)), `./run.sh` starts **clean-tts on 8010**, sets `TTS_PROVIDER=clean-xtts` for that session, then the API and frontend — **Voice** mode in the UI can use real speech. If there is no clean-tts venv, the API still follows `backend/.env` (e.g. `mock`). Use **`START_VOICE=0 ./run.sh`** to skip launching clean-tts (lighter machine).

**If your Mac feels slow or hot:** `./run.sh` already avoids the heaviest defaults (no API file-watcher reload; Next uses webpack on `127.0.0.1` only). Run **only one** service when possible: `./run-backend.sh` or `./run-frontend.sh` in separate terminals. **Quit Ollama** when you are not chatting (`ollama stop` / Activity Monitor) — local LLMs use a lot of RAM. **Skip Docker** unless you need the full container stack.

**Ollama is optional.** If [Ollama](https://ollama.com) is not running, the app still responds using the excerpt fallback. For full chat + semantic retrieval, run Ollama locally and pull `qwen2.5:3b` and `nomic-embed-text` (see below).

To turn API auto-reload back on while editing Python: `DEV_RELOAD=1 ./run.sh`.

### Prerequisites

- **Docker & Docker Compose** (optional; heavier on some Macs)
- **Or**: Node.js 20+, Python 3.11+, npm; Ollama optional for full LLM features

### Option 1: Docker (Fastest, includes Ollama)

```bash
# Clone and enter repo
git clone <repo-url>
cd sai-s-PersonaRAG

# Start all services (including Ollama)
docker compose up --build

# This will:
# 1. Start Ollama service on port 11434
# 2. Start backend (FastAPI) on port 8000
# 3. Start frontend (Next.js) on port 3000

# On first run, models will be pulled:
#   - qwen2.5:3b (chat model, ~2GB)
#   - nomic-embed-text (embedding model, ~300MB)

# Access application
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# Health:    http://localhost:8000/health
```

### Option 2: Local Development (Requires Ollama)

**Install Ollama locally first:**

```bash
# macOS
brew install ollama
ollama serve  # Start daemon in terminal 1

# Linux / Windows
# Download from https://ollama.ai

# Pull required models (one-time setup)
ollama pull qwen2.5:3b
ollama pull nomic-embed-text

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

**Backend:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Ensure Ollama variables are set
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_CHAT_MODEL=qwen2.5:3b
# OLLAMA_EMBED_MODEL=nomic-embed-text

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest
```

**Frontend:**

```bash
cd frontend
npm install
cp .env.example .env.local

# Development mode
npm run dev

# Access at http://localhost:3000
```

## How It Works

### 1. Data Ingestion

**Input**: Markdown files in `data/raw/` (e.g., resume, projects, skills)

**Process** (`scripts/ingest.py`):
```python
python3 scripts/ingest.py \
  --max-chars 1200 \      # Chunk size
  --overlap 120           # Overlapping chars for context
```

**Output**: `data/processed/chunks.json`
```json
{
  "chunks": [
    {
      "id": "work_experience_00001",
      "content_type": "work_experience",
      "source_file": "work_experience.md",
      "section_title": "Senior Engineer at Acme",
      "text": "Led team of 5 engineers...",
      "metadata": { ... }
    },
    ...
  ]
}
```

**Why this approach:**
- Markdown is human-editable (version control friendly)
- Chunks preserve source, section, and metadata for citations
- Flexible chunking strategy (tunable overlap, size)

### 2. Retrieval & Chat Flow

```
User Question
    │
    ├─> Retrieve top-k chunks (TF-IDF or Ollama embeddings)
    │
    ├─> Call Ollama with context + conversation history
    │   └─> Receive JSON response (answer + confidence + citations)
    │       └─> If Ollama unavailable: fallback to excerpt mode
    │
Response (same schema either way):
{
  "answer": "I led a team of 5 engineers...",
  "confidence": "high" | "medium" | "low",
  "sources": [...],                          # Cited chunks
  "grounding_note": null | "retrieval weak",
  "session_id": "abc123",
  "retrieval": [...],                        # All hits (debug)
}
```

### 3. Session Memory

Conversations are bounded in size:

```
Per session_id:
  - Max 12 messages
  - Max 4000 total characters
  - Older turns are dropped when limits exceeded

Benefits:
  - Memory-safe (no unbounded growth)
  - Fast lookup (in-process dict)
  - Easy to swap Redis later (same HTTP contract)
```

## Configuration

### Environment Variables

**Backend** (`backend/.env`):

```bash
# Application
APP_NAME=ai-portfolio-agent API
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO

# Ollama local LLM setup (required)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:3b
OLLAMA_EMBED_MODEL=nomic-embed-text

# Retrieval
RETRIEVAL_BACKEND=auto               # "tfidf" or "ollama"
RETRIEVAL_TOP_K=5
RETRIEVAL_WEAK_SCORE_THRESHOLD=0.06

# Session memory
SESSION_MAX_MESSAGES=12
SESSION_MAX_TOTAL_CHARS=4000

# TTS (placeholder; "mock" or "f5-tts" when ready)
TTS_PROVIDER=mock
```

**Frontend** (`frontend/.env.local`):

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Development Commands

### Backend

```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest                          # All tests
pytest tests/test_chat.py -v    # Specific file
pytest -k "test_retrieval" -v   # By keyword

# Data ingestion
python3 -m app.rag.ingest --max-chars 1200 --overlap 120

# Format & lint
black app/                      # Format
pytest --cov=app tests/         # Coverage
```

### Frontend

```bash
# Development
npm run dev

# Production build
npm run build
npm start

# Lint
npm run lint
```

### Docker

```bash
# API + Ollama only (e.g. Ubuntu VM; UI on Vercel)
docker compose up -d --build ollama backend
./scripts/vm-bootstrap.sh   # first time: pull models + ingest + restart backend

# Fresh Ubuntu VM (Docker + clone + models + ingest)
# After: ssh -i key.pem ubuntu@IP
#   bash scripts/oci-install.sh

# Full stack with local Next.js (profile required)
docker compose --profile local-ui up --build

# Optional: backend bind-mount for hot reload
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile local-ui up --build

# View logs
docker compose logs -f          # All services
docker compose logs -f backend  # Specific service

# Run tests in container
docker compose exec backend pytest

# Stop everything
docker compose down
```

**Vercel + VM API:** Open OCI port **8000** to the internet (or terminate TLS on 443). On Vercel set `NEXT_PUBLIC_API_BASE_URL` and `BACKEND_ORIG` to the same API base (e.g. `http://YOUR_PUBLIC_IP:8000`). In repo-root `.env` set `CORS_ORIGINS=https://your-app.vercel.app` for compose (see `compose.env.example`). The Next.js client calls same-origin `/api/*`; rewrites proxy to your VM.

See [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md) for advanced Docker workflows.

## Future Enhancements

### Text-to-Speech (In Progress)

Placeholder infrastructure ready for **F5-TTS** local voice synthesis:

- **Route**: `POST /api/tts` (text → audio metadata)
- **Status**: Currently mocked; returns deterministic audio URLs
- **Integration**: Swap `MockTTSBackend` with `F5TTSBackend` when model is available
- **No breaking changes**: HTTP contract stays the same

See [docs/TTS_INTEGRATION_GUIDE.md](docs/TTS_INTEGRATION_GUIDE.md) for implementation roadmap.

### Planned Improvements

- [ ] **Vector database**: Replace in-memory index with Pinecone/Weaviate
- [ ] **Redis session store**: Swap in-memory sessions for distributed Redis
- [ ] **Streaming responses**: WebSocket support for real-time answer generation
- [ ] **Multi-voice TTS**: Voice profile management when F5-TTS integrated
- [ ] **Metrics & monitoring**: Prometheus, structured JSON logging
- [ ] **Frontend E2E tests**: Playwright/Cypress coverage
- [ ] **API authentication**: Token-based access control if needed

## Known Limitations

1. **In-memory retrieval**: Full-text index rebuilt on each startup (fine for ~100 chunks; swap for vector DB at scale)
2. **Session memory**: Bounded, in-process (use Redis for multi-server deployments)
3. **No user authentication**: Open portfolio; add OAuth/JWT if restricting access
4. **TTS not integrated**: Placeholder architecture only; F5-TTS model integration pending
5. **Single-source data**: Reads from `chunks.json`; add incremental updates/versioning as needed

## Demo Notes

**Expected behavior:**

1. **With Ollama running** (normal operation):
   - Answers use Qwen 2.5 with retrieval grounding
   - High confidence when chunks are relevant
   - Natural language, grounded in your data
   - Supports local embedding search (nomic-embed-text)

2. **If Ollama unavailable** (graceful degradation):
   - Answers fallback to excerpts from best-matching chunks (TF-IDF)
   - Confidence is always "low"
   - Still accurate and transparent

**Example questions:**
- "Tell me about your ML experience"
- "What's your background in backend systems?"
- "Describe a time you led a team"
- "What technologies do you know?"

**Try:**
- Ask follow-ups (uses session history)
- Note the "sources" and "retrieval" sections (shows reasoning)
- Check confidence levels (reflects answer quality)

## Testing

```bash
# Backend test suite
cd backend
pytest                          # All tests
pytest -v                       # Verbose
pytest --cov=app tests/         # Coverage

# Test modules:
# - test_health.py       → /health endpoint
# - test_chat.py         → /api/chat endpoint
# - test_retrieval.py    → Semantic search
# - test_chunking.py     → Data ingestion
# - test_chat_session.py → Session memory
# - test_ingest.py       → Markdown → chunks
```

## Troubleshooting

**Ollama not running / connection refused:**
```bash
# Check if Ollama service is running
curl http://localhost:11434/api/tags

# If not, start it:
# macOS: brew services start ollama
# Or run: ollama serve

# Verify models are pulled
ollama list
# Should show: qwen2.5:3b and nomic-embed-text

# Pull models if missing
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

**Backend won't start:**
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Install/update dependencies
pip install -r requirements.txt --upgrade

# Test import
python3 -c "from app.main import app; print('OK')"

# Verify Ollama URL is correct
# OLLAMA_BASE_URL=http://localhost:11434
```

**Frontend can't reach backend:**
```bash
# Verify NEXT_PUBLIC_API_BASE_URL
cat frontend/.env.local

# Should match your backend URL (http://localhost:8000 for local dev)
```

**Docker container fails to build:**
```bash
# Rebuild from scratch
docker compose down
docker system prune -a
docker compose up --build

# Check logs
docker compose logs backend
docker compose logs ollama

# If Ollama is stuck downloading models, check disk space
docker system df
```

See [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md) for more troubleshooting.

## Contributing

This is a personal portfolio project. To adapt for your own use:

1. **Replace data**: Update `data/raw/*.md` with your professional content
2. **Customize sections**: Add/remove markdown files as needed
3. **Tune retrieval**: Adjust `RETRIEVAL_TOP_K`, chunking parameters, or switch to TF-IDF backend
4. **Customize LLM**: Modify `OLLAMA_CHAT_MODEL` (e.g., `mistral:7b`, `neural-chat`) in config

## License

Personal project. Use freely for your own portfolio.

## Documentation

- [Architecture & Design](docs/architecture.md) — System overview, boundaries, extension points
- [Content Strategy](docs/content_strategy.md) — How to organize professional data
- [TTS Integration](docs/TTS_INTEGRATION_GUIDE.md) — F5-TTS roadmap and integration guide
- [Docker Setup](docs/DOCKER_SETUP.md) — Advanced container workflows

**Backend**

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional; defaults match .env.example
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run tests (with the same venv activated, from `backend/`):

```bash
pytest
```

**Ingestion** (builds `data/processed/chunks.json` from `data/raw/`):

From the repository root:

```bash
python3 scripts/ingest.py
```

Or from `backend/`:

```bash
python3 -m app.rag.ingest
```

Optional: `INGEST_REPO_ROOT=/path/to/repo` if you run the module from another working directory. Use `--max-chars` and `--overlap` to tune chunk size. The output shape is illustrated in `data/processed/chunks.sample.json`.

**Retrieval** (chat uses RAG over `data/processed/chunks.json`):

- Default: **TF–IDF** + cosine similarity (no API key). Set `RETRIEVAL_BACKEND=tfidf` to force it.
- With **`OPENAI_API_KEY`**: `RETRIEVAL_BACKEND=auto` uses OpenAI embeddings (`OPENAI_EMBEDDING_MODEL`, `OPENAI_BASE_URL`).
- **`OPENAI_CHAT_MODEL`** (e.g. `gpt-4o-mini`) powers grounded answers; without a key, the API returns excerpt-only fallbacks with citations.
- `CHUNKS_JSON_PATH` overrides the default path to `chunks.json`.

API routes: `GET /health`, `POST /api/chat` (JSON body: `question`, optional `session_id`; response includes grounded `answer`, `confidence`, `sources`, `grounding_note`, `retrieval`, optional `retrieval_error`).

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

`NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` points at the API (default `http://localhost:8000`).

`npm install` needs enough free disk space for `node_modules`. If it fails with `ENOSPC`, free space and retry.

Copy `.env.example` to `.env` at the repo root for frontend-related vars. For the API, copy `backend/.env.example` to `backend/.env` if you want to override defaults.

## Docker (Local Development)

The fastest way to run both frontend and backend locally is with Docker Compose.

**Prerequisites**

- Docker and Docker Compose installed

**Quick start**

```bash
# From the repository root — local Next.js + API
docker compose --profile local-ui up --build

# API + Ollama only (frontend hosted on Vercel)
docker compose up -d --build ollama backend
```

This builds and starts:
- **Backend**: http://localhost:8000 (FastAPI)
- **Frontend** (with `--profile local-ui`): http://localhost:3000 (Next.js)

Health check endpoint: `curl http://localhost:8000/health`

**Common commands**

```bash
# Start services in background
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend

# Rebuild after dependency changes
docker compose up --build

# Run backend tests in container
docker compose exec backend pytest

# Run backend ingestion in container
docker compose exec backend python -m app.rag.ingest --repo-root /app

# Drop into backend shell for debugging
docker compose exec backend /bin/bash
```

**Environment variables**

Backend settings are configured via `backend/.env` (copy from `backend/.env.example`):

```bash
# backend/.env
OPENAI_API_KEY=sk-...  # Optional; enables OpenAI embeddings & LLM
TTS_PROVIDER=mock      # "mock" or "f5-tts" when available
```

Frontend settings are configured via `frontend/.env.local` (copy from `frontend/.env.example`):

```bash
# frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**Development workflow**

Default compose mounts only **`data/` → `/app/data`** (VM-ready). Rebuild the backend image after code changes, or add **`docker-compose.dev.yml`** to bind-mount `backend/app` for hot reload.

For production-like local UI, run `docker compose --profile local-ui up --build` and open http://localhost:3000.

## Future voice support

The backend includes placeholder infrastructure for **Text-to-Speech (TTS)** synthesis. Currently:

- **Route**: `POST /api/tts` (text → audio metadata)
- **Status**: Mocked responses for frontend development
- **Configuration**: `TTS_PROVIDER=mock` (env var)

When ready to integrate **F5-TTS** (or another local model):

1. Implement a real `F5TTSBackend` in `backend/app/services/tts_service.py`
2. Set `TTS_PROVIDER=f5-tts` to activate it
3. No breaking changes to the API contract

See [docs/architecture.md](docs/architecture.md#tts-architecture) for details.

## Documentation

See [docs/architecture.md](docs/architecture.md) for a high-level system view.
