# Architecture

## Overview

The product is a **recruiter-facing portfolio** with a **question-and-answer** flow backed by **retrieval-augmented generation (RAG)** over curated professional content (resume, project notes, skills, experience).

Voice cloning is **out of scope** for the initial scaffold and can attach later as a separate client or pipeline stage.

## Components

1. **Frontend (`frontend/`)**  
   Next.js UI for browsing the portfolio and asking questions. Calls the backend over HTTP (REST or future streaming).

2. **Backend (`backend/`)**  
   FastAPI service: orchestrates retrieval, optional LLM calls, and response shaping. Bounded **session memory** (`session_id`) is in-process today (`InMemorySessionStore`); swap for Redis without changing the HTTP contract.

3. **Data (`data/`)**  
   - `raw/`: human-edited or exported source material (see [content_strategy.md](content_strategy.md) for topic files and retrieval intent).  
   - `processed/`: `chunks.json` produced by `scripts/ingest.py` (or `python -m app.rag.ingest` from `backend/`); embeddings and vector indexes can live alongside later.

4. **Retrieval layer**  
   In-memory index over `data/processed/chunks.json`: TF–IDF (keyword-based, no external API) or Ollama embeddings (using local `nomic-embed-text` model). A hosted vector DB can replace `RetrievalBackend` later.

5. **Answer generation**  
   `backend/app/services/llm_service.py` calls Ollama's local `qwen2.5:3b` model over HTTP for structured JSON responses; if the model is unavailable, it returns an honest excerpt-based fallback with the same citation shape. Prompts live in `prompts.py`.

6. **Text-to-Speech (TTS) — future voice support**  
   `backend/app/services/tts_service.py` provides a clean abstraction for synthesizing answers into audio. Currently uses a mock backend for development. When ready, a real **F5-TTS** backend will plug in without changing the `/api/tts` HTTP contract. See [TTS Architecture](#tts-architecture) below.

## TTS Architecture

### Current state (mock)

- **Route**: `POST /api/tts` accepts `text` and optional `voice_profile_id`
- **Backend**: `MockTTSBackend` returns deterministic mocked audio metadata (URL, duration, etc.)
- **Schemas**: `TTSRequest` and `TTSResponse` in `backend/app/schemas/tts.py`
- **Config**: `TTS_PROVIDER` env var (default: `"mock"`)

### Future F5-TTS integration

When the F5-TTS model is available:

1. Download model artifacts and cache them locally
2. Load model in app startup (FastAPI lifespan event)
3. Implement `F5TTSBackend` in `tts_service.py` with the same interface
4. Switch `TTS_PROVIDER="f5-tts"` at runtime
5. Audio files stored locally or streamed directly to frontend

**No breaking changes**: All producers (route), consumers (frontend), and contracts remain unchanged.

## Boundaries

- **Frontend** does not own business rules for RAG; it sends questions and renders answers (and citations when available).
- **Backend** owns orchestration and can swap embedding models or vector stores without changing the frontend contract if HTTP shapes stay stable.
- **Scripts** hold offline jobs (ingest, reindex) so they are not mixed into request handlers.
- **TTS** is decoupled from chat logic; answers are generated independently, and voice synthesis is optional downstream.

## Extension points

- Add ingestion scripts under `scripts/` and write artifacts to `data/processed/`.
- Add retrieval and LLM configuration via environment variables (see `.env.example` patterns).
- Replace placeholder `docker-compose.yml` with real `frontend` / `backend` (and optional DB) services when deploying.
- Integrate F5-TTS backend by implementing `F5TTSBackend` in `tts_service.py` and setting `TTS_PROVIDER="f5-tts"`.
- Add audio caching layer (e.g., Redis or local file store) if synthesis latency becomes an issue.
