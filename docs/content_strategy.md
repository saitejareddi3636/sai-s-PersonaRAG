# Content strategy for retrieval

This document explains how the files under `data/raw/` are intended to feed a future ingestion and RAG pipeline. It is not an implementation spec; it aligns author intent with retrieval behavior.

## File map

| File | Purpose in retrieval |
|------|----------------------|
| `summary.md` | Short narrative and “what to emphasize”; use for high-level answers and tone, not as the only source of facts. |
| `work_experience.md` | Evidence for employers, scope, stack, and responsibilities; primary source for “tell me about your background” and role-specific follow-ups. |
| `projects.md` | Concrete work samples; good for “describe a project,” tradeoffs, and technical depth questions. |
| `skills.md` | Structured capability inventory; pair with experience for “what technologies do you use” without inventing proficiency. |
| `education.md` | Degrees and credentials; use when asked about formal background or certifications. |
| `achievements.md` | Verifiable highlights; use sparingly and only when the question asks for awards, talks, or publications. |
| `target_roles.md` | Job-search intent, seniority, location, domains; primary source for “what are you looking for” and fit questions. |
| `faq_for_recruiters.md` | Pre-written Q&A pairs for common recruiter screens; high precision for matching questions if chunks are aligned to pairs. |

## Design choices for chunking

- **One topic per file** keeps provenance clear: citations can point to a single document type (e.g. “projects” vs “work experience”).
- **Repeated headings** (`##` for jobs, projects, FAQ entries) give stable boundaries for a splitter (by heading, by horizontal rule, or by max token size with overlap).
- **Markdown** is easy to transform: strip front matter if you add it later, normalize lists, and pass plain text to the embedder.
- **Tables** (e.g. in `skills.md`) can be flattened to text during ingestion or kept as markdown for models that handle tables well.

## How ingestion should use these files

The repo implements a first pass in `backend/app/rag/ingest.py`: it reads `*.md` and `*.json` from `data/raw/`, splits markdown by `#`–`###` headings, sub-chunks long sections by paragraph and size, and writes `data/processed/chunks.json` (see `data/processed/chunks.sample.json` for the output shape). Run from the repo root: `python3 scripts/ingest.py`.

Downstream steps you may add later:

1. **Embed** chunks and store in a vector index with metadata for filtering (e.g. `content_type` from the filename stem).
2. **Write embeddings / index manifests** under `data/processed/` alongside `chunks.json`—keep raw markdown as the human-edited source of truth.

## Grounding and safety

- **Do not invent metrics** in source files; the assistant should reflect what you authored. If a field is still a placeholder, retrieval will surface bracketed placeholders—replace them before production use.
- **Prefer multiple citations** for answers that combine summary, experience, and skills so the model does not overfit a single file.
- **FAQ vs narrative:** `faq_for_recruiters.md` is optimized for near-duplicate question matching; open-ended questions should still pull from `work_experience.md` and `projects.md`.

## Maintenance

- When you change roles or goals, update `target_roles.md` and `summary.md` together so retrieved answers stay consistent.
- Version or date-stamp large edits if you need to debug retrieval drift later (optional file `CHANGELOG` or git history is enough for many teams).
