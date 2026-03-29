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
   In-memory index over `data/processed/chunks.json`: TF–IDF by default, or OpenAI embeddings when `OPENAI_API_KEY` is set (`backend/app/rag/`). A hosted vector DB can replace `RetrievalBackend` later.

5. **Answer generation**  
   `backend/app/services/llm_service.py` calls OpenAI chat completions with JSON output when `OPENAI_API_KEY` is set; otherwise it returns an honest excerpt-based fallback with the same citation shape. Prompts live in `prompts.py`.

## Boundaries

- **Frontend** does not own business rules for RAG; it sends questions and renders answers (and citations when available).
- **Backend** owns orchestration and can swap embedding models or vector stores without changing the frontend contract if HTTP shapes stay stable.
- **Scripts** hold offline jobs (ingest, reindex) so they are not mixed into request handlers.

## Extension points

- Add ingestion scripts under `scripts/` and write artifacts to `data/processed/`.
- Add retrieval and LLM configuration via environment variables (see `.env.example` patterns).
- Replace placeholder `docker-compose.yml` with real `frontend` / `backend` (and optional DB) services when deploying.
