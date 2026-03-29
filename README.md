# ai-portfolio-agent

Monorepo for a recruiter-facing AI portfolio: visitors ask questions about skills, projects, and experience; answers are grounded in professional data via retrieval (RAG). Voice features may be added later.

## Layout

| Path | Role |
|------|------|
| `frontend/` | Next.js (TypeScript, Tailwind) |
| `backend/` | FastAPI API |
| `data/raw/` | Structured markdown for your profile (one file per topic); see `docs/content_strategy.md` |
| `data/processed/` | Processed chunks (`chunks.json` from ingestion; see `chunks.sample.json`) |
| `docs/` | Architecture and design notes |
| `scripts/` | One-off automation (ingest, deploy helpers) |

## Prerequisites

- Node.js 20+ and npm (or pnpm/yarn if you standardize on one)
- Python 3.11+

## Local development

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

## Docker

`docker-compose.yml` is a placeholder until services are defined.

## Documentation

See [docs/architecture.md](docs/architecture.md) for a high-level system view.
