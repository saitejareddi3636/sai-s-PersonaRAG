# Docker Setup Guide

This guide covers running the PersonaRAG application with Docker for local development.

## Quick Start

```bash
# From repository root
docker compose up --build
```

This will:
1. Build backend image with FastAPI
2. Build frontend image with Next.js
3. Start both services with proper networking
4. Health-check the backend before starting frontend

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Health**: http://localhost:8000/health

## Architecture

```
┌─────────────────┐
│   localhost:3000│
│    Frontend     │ (Next.js)
│   (node:20)     │
└────────┬────────┘
         │
         │ http://localhost:8000
         │ (NEXT_PUBLIC_API_BASE_URL)
         │
┌────────┴────────┐
│  localhost:8000 │
│    Backend      │ (FastAPI)
│  (python:3.11)  │
│   personarag    │
│    -network     │
└─────────────────┘
         │
         └─> data/ (shared volume)
```

## Service Definitions

### Backend (`backend/Dockerfile`)

- **Base image**: `python:3.11-slim`
- **Port**: 8000
- **Entrypoint**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Health check**: `curl http://localhost:8000/health`

**Volumes mounted**:
- `./backend/app:/app/app` — Code reloading (uvicorn auto-reloads on file changes)
- `./data:/app/data` — Shared data directory (chunks.json, raw markdown)

**Environment**:
- See `backend/.env` (copy from `backend/.env.example`)
- Key variables:
  - `OLLAMA_BASE_URL=http://ollama:11434` — Local Ollama service (Docker network)
  - `OLLAMA_CHAT_MODEL=qwen2.5:3b` — Chat model name
  - `OLLAMA_EMBED_MODEL=nomic-embed-text` — Embedding model
  - `RETRIEVAL_BACKEND=auto` — Auto uses Ollama embeddings or TF-IDF fallback
  - `TTS_PROVIDER` — "mock" (default) or "f5-tts" (when integrated)

### Frontend (`frontend/Dockerfile`)

- **Base image**: `node:20-alpine` (multi-stage build)
- **Port**: 3000
- **Entrypoint**: `npm start` (production Next.js server)

**Build stages**:
1. **Builder**: Installs dependencies, builds Next.js app
2. **Runtime**: Minimal image with production deps only

**Environment**:
- See `frontend/.env.local` (copy from `frontend/.env.example`)
- Key variable:
  - `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` — Points frontend to backend

**Depends on**: Backend service (with healthcheck)

## Development Workflow

### Edit & Reload

**Backend code changes**:
- Edit files in `backend/app/`
- uvicorn detects changes and auto-reloads
- No container restart needed

**Frontend code changes**:
- Edit files in `frontend/app/` or `frontend/components/`
- Next.js development server would auto-reload (for dev mode)
- Current Dockerfile runs production build; for hot-reload, create `Dockerfile.dev`

### Common Tasks

**View logs**:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

**Stop services**:
```bash
docker compose down
```

**Remove containers, networks, images**:
```bash
docker compose down --volumes --rmi all
```

**Run backend tests**:
```bash
docker compose exec backend pytest
```

**Run data ingestion**:
```bash
docker compose exec backend python3 -m app.rag.ingest
```

**Access backend shell**:
```bash
docker compose exec backend /bin/bash
```

**Rebuild specific service**:
```bash
docker compose build backend --no-cache
docker compose up
```

## Environment Variables

### Backend (`backend/.env`)

Template (copy from `backend/.env.example`):

```dotenv
# Application
APP_NAME=ai-portfolio-agent API
CORS_ORIGINS=http://localhost:3000,http://frontend:3000
LOG_LEVEL=INFO

# Retrieval & Embeddings (Ollama local stack)
RETRIEVAL_BACKEND=auto
RETRIEVAL_TOP_K=5
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_CHAT_MODEL=qwen2.5:3b
OLLAMA_EMBED_MODEL=nomic-embed-text
RETRIEVAL_WEAK_SCORE_THRESHOLD=0.06

# Session memory
SESSION_MAX_MESSAGES=12
SESSION_MAX_TOTAL_CHARS=4000

# TTS
TTS_PROVIDER=mock
```

If `.env` is missing, `docker compose` will still start (using hardcoded defaults in `docker-compose.yml`).

### Frontend (`frontend/.env.local`)

Template (copy from `frontend/.env.example`):

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### Port already in use

If port 3000 or 8000 is already in use:

```bash
# Change ports in docker-compose.yml
# Or kill the process holding the port
lsof -i :3000          # List process on port 3000
kill -9 <PID>          # Kill by PID

# Or use different ports temporarily
docker compose -f docker-compose.yml \
  -e FRONTEND_PORT=3001 \
  -e BACKEND_PORT=8001 \
  up
```

### Backend health check failing

If frontend won't start (waiting for backend health):

```bash
# Check backend logs
docker compose logs backend

# Common issues:
# - Missing dependencies → docker compose build backend --no-cache
# - Import errors → docker compose exec backend python3 -c "from app.main import app"
# - Port conflict → docker compose down && docker compose up
```

### Frontend can't reach backend

If frontend shows network errors:

```bash
# Verify frontend environment variable
docker compose exec frontend env | grep NEXT_PUBLIC_API_BASE_URL

# Should output: NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Check network connectivity from frontend container
docker compose exec frontend curl http://backend:8000/health
```

### Docker image size too large

Frontend image can be large due to build artifacts. To optimize:

1. Add `frontend/.dockerignore` entries
2. Use minimal base images (already using `node:20-alpine`)
3. Consider multi-stage builds more aggressively

### Clean rebuild

If images are stale or corrupted:

```bash
docker compose down
docker system prune -a        # Remove all unused images
docker compose up --build     # Rebuild from scratch
```

## Development vs. Production

**Current setup** (`docker-compose.yml`):
- **Purpose**: Local development + testing
- **Frontend**: Production Next.js server (no hot-reload)
- **Backend**: FastAPI with code volume mounts (hot-reload on changes)

**For true hot-reload on frontend**, create `frontend/Dockerfile.dev`:

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci

EXPOSE 3000
CMD ["npm", "run", "dev"]
```

Then in `docker-compose.dev.yml`:
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile.dev
```

**For production**, use the current `Dockerfile` (optimized, minimal size).

## Networking

Services communicate via Docker's `personarag-network` bridge:

- **Frontend** → **Backend**: Via `http://localhost:8000` (from host perspective) or `http://backend:8000` (from container perspective)
- **Shared data**: Both mount `./data:/app/data`, allowing them to read/write the same files

The frontend receives `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` so the browser (on host) can reach the backend.

## Next Steps

1. **Run locally**: `docker compose up --build`
2. **Verify health**: `curl http://localhost:8000/health`
3. **Test chat**: Open http://localhost:3000 and ask a question
4. **Check logs**: `docker compose logs -f`
5. **Iterate**: Edit backend code and watch uvicorn auto-reload
6. **Deploy**: Use same Dockerfiles for staging/production (with `.env` secrets injected)
